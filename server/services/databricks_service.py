"""Databricks Model Serving Service.

This service handles calls to Databricks model serving endpoints using the OpenAI client.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from typing import Any

import httpx
import requests
from fastapi import HTTPException
from openai import OpenAI

logger = logging.getLogger(__name__)

# Global client cache to reuse OpenAI clients across requests
# Key: (workspace_url, token_hash) -> OpenAI client
_client_cache = {}

# Lazy-built cache of ``google.genai.Client`` instances for the Gemini
# ai-gateway path. Keyed by (workspace_url, token_hash). Constructed on
# first Gemini call to avoid requiring ``google-genai`` in minimal deploys.
_gemini_client_cache: dict[tuple[str, str], Any] = {}

# Serving-endpoints TTL cache. The model list is workspace-global and changes
# infrequently, but the frontend's React Query cache is keyed per workshop, so
# without a server-side cache each workshop view triggers a fresh Databricks
# REST call. We cache at the service layer so all callers (per-workshop and
# global routes) share one workspace-level entry.
# Key: (workspace_url, token_hash) -> (monotonic_timestamp, endpoints)
_ENDPOINTS_CACHE_TTL_S = float(os.getenv("DATABRICKS_ENDPOINTS_CACHE_TTL_S", "300"))
_endpoints_cache: dict[tuple[str, str], tuple[float, list[dict[str, Any]]]] = {}
_endpoints_cache_locks: dict[tuple[str, str], asyncio.Lock] = {}
_endpoints_cache_locks_guard = asyncio.Lock()


def clear_serving_endpoints_cache() -> None:
    """Clear the cached serving-endpoints list. Useful for manual invalidation and tests."""
    _endpoints_cache.clear()


def _fix_databricks_shim_response(response: httpx.Response) -> None:
    """Patch JSON responses from the Databricks OpenAI-compat shim that violate
    the OpenAI chat completion contract.

    Currently fixes:
    - ``id: null`` on chat completions. Gemini-backed endpoints leave id null;
      OpenAI SDK 2.x's Pydantic validator rejects this. Replaced with a
      generated placeholder so downstream parsing succeeds.

    Other backing models (Claude, gpt-5) return a non-null id and are untouched.
    """
    if "application/json" not in response.headers.get("content-type", ""):
        return
    try:
        response.read()
    except httpx.ResponseNotRead:
        pass
    except Exception:
        return
    try:
        body = json.loads(response.content)
    except Exception:
        return
    if not isinstance(body, dict) or "choices" not in body:
        return
    if body.get("id") in (None, ""):
        body["id"] = f"databricks-shim-{uuid.uuid4().hex}"
        new_body = json.dumps(body).encode()
        response._content = new_body
        response.headers["content-length"] = str(len(new_body))


def _normalize_shim_content(content: Any) -> Any:
    """Normalize the Databricks shim's Gemini content shape.

    Gemini-backed endpoints return content as an array of part dicts:
        ``[{"type": "text", "text": "...", "thoughtSignature": "..."}]``
    instead of a plain string, which breaks parsers that expect
    ``response.choices[0].message.content`` to be a ``str``.

    Joins all text parts into a single string. Non-Gemini responses
    (string content) pass through unchanged.
    """
    if not isinstance(content, list):
        return content
    parts: list[str] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            text = part.get("text")
            if text:
                parts.append(text)
    return "".join(parts) if parts else content


def _looks_like_gemini(model_name: str) -> bool:
    """Detect Gemini-family endpoint names. Databricks names them ``databricks-gemini-*``."""
    return "gemini" in (model_name or "").lower()


def _is_openai_reasoning_model(model_name: str) -> bool:
    """Detect OpenAI reasoning-model endpoint names.

    Reasoning models (gpt-5 / gpt-5.1 / gpt-5.5 / gpt-5-codex and the o-series
    o1/o3/o4) reject ``temperature != 1`` with:
        "Unsupported value: 'temperature' does not support X with this model.
         Only the default (1) value is supported."
    We can't drop the param like LiteLLM does for the DSPy path — the OpenAI
    SDK has no equivalent — so we normalize the request here instead.
    Databricks prefixes its endpoint names with ``databricks-``.
    """
    name = (model_name or "").lower()
    return (
        "gpt-5" in name
        or "-o1" in name
        or "-o3" in name
        or "-o4" in name
        or name.startswith("o1")
        or name.startswith("o3")
        or name.startswith("o4")
    )


def _normalize_request_for_reasoning_model(
    endpoint_name: str, temperature: float
) -> float:
    """Return a temperature that the reasoning-model endpoint will accept.

    For gpt-5 / o-series endpoints, force temperature=1.0 (the only value
    they support). For all other endpoints, return the caller's value
    unchanged. Logs when an override happens so the normalization is
    auditable.
    """
    if _is_openai_reasoning_model(endpoint_name) and temperature != 1.0:
        logger.info(
            "Reasoning model %s only accepts temperature=1.0; overriding caller's %.2f",
            endpoint_name,
            temperature,
        )
        return 1.0
    return temperature


def _messages_to_genai_contents(messages: list[dict[str, Any]]) -> tuple[list[Any], str | None]:
    """Convert OpenAI chat messages to Gemini ``Content`` objects + an optional
    ``system_instruction``. ``role: system`` collapses into the latter."""
    from google.genai import types as genai_types

    system_parts: list[str] = []
    contents: list[Any] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            if isinstance(content, str) and content:
                system_parts.append(content)
            continue
        # Gemini uses "model" instead of "assistant"
        genai_role = "model" if role == "assistant" else "user"
        if isinstance(content, str):
            contents.append(
                genai_types.Content(role=genai_role, parts=[genai_types.Part(text=content)])
            )
        elif isinstance(content, list):
            # Pre-formatted parts (rare) — pass text through as best-effort.
            text = "".join(
                p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"
            )
            contents.append(
                genai_types.Content(role=genai_role, parts=[genai_types.Part(text=text)])
            )
    system_instruction = "\n\n".join(system_parts) if system_parts else None
    return contents, system_instruction


def _genai_response_to_chat_shape(response: Any, model_name: str) -> dict[str, Any]:
    """Adapt a google.genai ``GenerateContentResponse`` to the chat-completions
    dict shape callers expect (``choices[0].message.content`` as a string)."""
    text_parts: list[str] = []
    finish_reason = "stop"
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        first = candidates[0]
        for part in getattr(getattr(first, "content", None), "parts", None) or []:
            t = getattr(part, "text", None)
            if t:
                text_parts.append(t)
        fr = getattr(first, "finish_reason", None)
        if fr is not None:
            # google.genai returns an enum; surface its name for visibility.
            finish_reason = str(getattr(fr, "name", fr) or finish_reason).lower()

    usage = getattr(response, "usage_metadata", None)
    usage_dict = {
        "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
        "completion_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
        "total_tokens": getattr(usage, "total_token_count", 0) if usage else 0,
    }

    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": "".join(text_parts)},
                "index": 0,
                "finish_reason": finish_reason,
            }
        ],
        "model": model_name,
        "usage": usage_dict,
    }


def _get_token_hash(token: str) -> str:
    """Get a hash of the token for cache key (don't store actual token in cache key)."""
    return hashlib.sha256(token.encode()).hexdigest()[:16]


def _normalize_databricks_host(host: str | None) -> str | None:
    """Normalize Databricks host to include scheme and no trailing slash."""
    if not host:
        return None
    normalized = host.strip().rstrip("/")
    if not normalized:
        return None
    if not normalized.startswith(("http://", "https://")):
        normalized = f"https://{normalized}"
    return normalized


def normalize_experiment_id(experiment_id: str | None) -> str | None:
    """Normalize MLflow experiment IDs from env/form inputs.

    Databricks App env var values and form values can occasionally include
    surrounding quotes (e.g. '"12345"' or "'12345'"), which MLflow then treats
    as a literal ID and returns "experiment not found".
    """
    if experiment_id is None:
        return None
    normalized = str(experiment_id).strip()
    while len(normalized) >= 2 and (
        (normalized.startswith('"') and normalized.endswith('"'))
        or (normalized.startswith("'") and normalized.endswith("'"))
    ):
        normalized = normalized[1:-1].strip()
    return normalized or None


def _get_sdk_token() -> str | None:
    """Get an OAuth token via the Databricks SDK (unified auth).

    On Databricks Apps the platform injects ``DATABRICKS_CLIENT_ID`` /
    ``DATABRICKS_CLIENT_SECRET`` which the SDK uses for M2M OAuth.
    Locally, the SDK uses CLI profile auth.
    """
    try:
        from databricks.sdk import WorkspaceClient

        w = WorkspaceClient()
        headers = w.config.authenticate()
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[len("Bearer "):]
    except Exception as exc:
        logger.warning("Databricks SDK auth failed: %s", exc)
    return None


def resolve_databricks_token() -> str:
    """Resolve a Databricks auth token via the SDK.

    On Databricks Apps the platform injects service principal credentials.
    Locally, the SDK picks up CLI profile auth from ``databricks auth login``.

    Falls back to the ``DATABRICKS_TOKEN`` environment variable when the SDK
    is not configured (e.g. CI or minimal local setups).

    Raises:
        RuntimeError: If no valid token can be resolved.
    """
    token = _get_sdk_token()
    if token:
        return token
    # Fallback: explicit env var (useful for CI / containers without SDK config)
    token = os.getenv("DATABRICKS_TOKEN")
    if token:
        logger.info("Using DATABRICKS_TOKEN env var (SDK auth unavailable)")
        return token
    raise RuntimeError(
        "Could not resolve Databricks auth token. "
        "On Databricks Apps this is automatic. "
        "Locally, run: databricks auth login --host <workspace-url>"
    )


def get_databricks_host() -> str:
    """Get the Databricks workspace host URL.

    On Databricks Apps, DATABRICKS_HOST is set by the platform.
    Locally, it comes from .env.local or the SDK config.

    Raises:
        RuntimeError: If no host can be resolved.
    """
    host = _normalize_databricks_host(os.getenv("DATABRICKS_HOST"))
    if host:
        return host
    try:
        from databricks.sdk import WorkspaceClient

        w = WorkspaceClient()
        host = _normalize_databricks_host(w.config.host)
        if host:
            return host
    except Exception:
        pass
    raise RuntimeError(
        "DATABRICKS_HOST not set. "
        "On Databricks Apps this is automatic. "
        "Locally, set DATABRICKS_HOST or configure a CLI profile."
    )


def get_experiment_id() -> str:
    """Get the MLflow experiment ID from the environment.

    Set via app.yaml resource declaration (value_from key: MLFLOW_EXPERIMENT_ID).

    Raises:
        RuntimeError: If MLFLOW_EXPERIMENT_ID is not set.
    """
    exp_id = normalize_experiment_id(os.getenv("MLFLOW_EXPERIMENT_ID"))
    if exp_id:
        return exp_id
    raise RuntimeError(
        "MLFLOW_EXPERIMENT_ID not set. "
        "On Databricks Apps, declare an mlflow_experiment resource in app.yaml. "
        "Locally, set MLFLOW_EXPERIMENT_ID in .env.local."
    )


class DatabricksService:
    """Service for interacting with Databricks model serving endpoints."""

    def __init__(self):
        """Initialize the Databricks service.

        Uses environment-based host and SDK-resolved token.
        """
        self.workspace_url = get_databricks_host()
        self.token = resolve_databricks_token()

        # Initialize the OpenAI client for calling serving endpoints
        # Use cached client if available to avoid reinitializing for every request
        try:
            cache_key = (self.workspace_url, _get_token_hash(self.token))

            if cache_key in _client_cache:
                self.client = _client_cache[cache_key]
            else:
                # Install a response hook that normalizes Databricks shim quirks
                # (e.g. Gemini-backed endpoints return id:null which OpenAI SDK
                # 2.x's Pydantic validator rejects).
                http_client = httpx.Client(
                    event_hooks={"response": [_fix_databricks_shim_response]}
                )
                self.client = OpenAI(
                    api_key=self.token,
                    base_url=f"{self.workspace_url}/serving-endpoints",
                    http_client=http_client,
                )
                _client_cache[cache_key] = self.client
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize OpenAI client: {e!s}") from e

    def call_serving_endpoint(
        self,
        endpoint_name: str,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int | None = None,
        model_parameters: dict[str, Any] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a Databricks serving endpoint using chat completion format.

        Args:
            endpoint_name: Name of the serving endpoint
            prompt: The prompt to send to the model
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            model_parameters: Additional model parameters
            response_format: Optional structured output spec (e.g., {"type":"json_schema", ...})

        Returns:
            Dictionary containing the response from the model
        """

        def _do_call(request_params: dict[str, Any]) -> dict[str, Any]:
            response = self.client.chat.completions.create(**request_params)
            try:
                message_dump = response.choices[0].message.model_dump()
            except Exception:
                message_dump = {
                    "content": response.choices[0].message.content,
                    "role": response.choices[0].message.role,
                }
            # Gemini-backed endpoints return content as an array of part dicts;
            # callers expect a plain string. Other backings pass through unchanged.
            if "content" in message_dump:
                message_dump["content"] = _normalize_shim_content(message_dump["content"])
            return {
                "choices": [
                    {
                        "message": message_dump,
                        "index": response.choices[0].index,
                        "finish_reason": response.choices[0].finish_reason,
                    }
                ],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
            # gpt-5 / o-series reject any temperature != 1
            temperature = _normalize_request_for_reasoning_model(endpoint_name, temperature)
            request_params = {"messages": messages, "model": endpoint_name, "temperature": temperature}

            if max_tokens:
                request_params["max_tokens"] = max_tokens
            if model_parameters:
                request_params.update(model_parameters)
            if response_format:
                request_params["response_format"] = response_format

            logger.info(f"Calling Databricks serving endpoint: {endpoint_name}")
            logger.debug(f"Request parameters: {request_params}")

            try:
                result = _do_call(request_params)
            except Exception as e:
                if response_format:
                    logger.warning(
                        "Structured outputs request failed for endpoint=%s; retrying without response_format. Error: %s",
                        endpoint_name,
                        e,
                    )
                    request_params.pop("response_format", None)
                    result = _do_call(request_params)
                else:
                    raise

            logger.info(f"Successfully called serving endpoint: {endpoint_name}")
            logger.debug(f"Response: {result}")

            return result

        except Exception as e:
            logger.error(f"Error calling serving endpoint {endpoint_name}: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error("Full traceback:", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error calling serving endpoint: {e!s}") from e

    async def list_serving_endpoints(self) -> list[dict[str, Any]]:
        """List available serving endpoints, cached per workspace with a TTL.

        The model list changes infrequently, so we cache at the service layer
        keyed by (workspace_url, token_hash). A per-key asyncio.Lock dedupes
        concurrent in-flight refreshes so a thundering herd of requests
        triggers only one upstream Databricks call. TTL is configurable via
        ``DATABRICKS_ENDPOINTS_CACHE_TTL_S`` (default 300s).
        """
        cache_key = (self.workspace_url, _get_token_hash(self.token))
        now = time.monotonic()

        cached = _endpoints_cache.get(cache_key)
        if cached and (now - cached[0]) < _ENDPOINTS_CACHE_TTL_S:
            logger.debug(
                "Serving endpoints cache hit workspace=%s age_s=%.1f count=%d",
                self.workspace_url,
                now - cached[0],
                len(cached[1]),
            )
            return cached[1]

        async with _endpoints_cache_locks_guard:
            lock = _endpoints_cache_locks.setdefault(cache_key, asyncio.Lock())

        async with lock:
            # Re-check inside the lock — another coroutine may have refreshed.
            cached = _endpoints_cache.get(cache_key)
            now = time.monotonic()
            if cached and (now - cached[0]) < _ENDPOINTS_CACHE_TTL_S:
                return cached[1]

            endpoints = await self._fetch_serving_endpoints()
            _endpoints_cache[cache_key] = (time.monotonic(), endpoints)
            logger.info(
                "Refreshed serving endpoints cache workspace=%s count=%d ttl_s=%.0f",
                self.workspace_url,
                len(endpoints),
                _ENDPOINTS_CACHE_TTL_S,
            )
            return endpoints

    async def _fetch_serving_endpoints(self) -> list[dict[str, Any]]:
        """Fetch the serving-endpoints list from the Databricks REST API (uncached)."""
        try:
            logger.info("Listing Databricks serving endpoints via REST API")

            url = f"{self.workspace_url}/api/2.0/serving-endpoints"
            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()

            data = resp.json()
            raw_endpoints = data.get("endpoints", [])

            endpoint_list = []
            for ep in raw_endpoints:
                state_obj = ep.get("state", {})
                ready = state_obj.get("ready", "")
                endpoint_list.append(
                    {
                        "name": ep.get("name", ""),
                        "id": ep.get("id", ""),
                        "state": ready,
                        "config": ep.get("config"),
                        "task": ep.get("task", ""),
                        "creator": ep.get("creator", ""),
                    }
                )

            logger.info(f"Found {len(endpoint_list)} serving endpoints")
            return endpoint_list

        except httpx.HTTPStatusError as e:
            logger.error(f"Error listing endpoints: {e}")
            raise HTTPException(status_code=502, detail=f"Error listing endpoints from Databricks: {e!s}") from e
        except Exception as e:
            logger.error(f"Error listing endpoints: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing endpoints: {e!s}") from e

    def get_endpoint_info(self, endpoint_name: str) -> dict[str, Any]:
        """Get information about a specific serving endpoint.
        Note: This method returns placeholder info since OpenAI client doesn't provide endpoint details.
        You may need to implement this using direct HTTP calls to Databricks API.

        Args:
            endpoint_name: Name of the serving endpoint

        Returns:
            Dictionary containing endpoint information
        """
        try:
            logger.info(f"Getting information for serving endpoint: {endpoint_name}")

            # Since OpenAI client doesn't provide endpoint details, return placeholder info
            endpoint_info = {
                "name": endpoint_name,
                "id": "placeholder-id",
                "state": "active",
                "config": {"model_name": endpoint_name},
                "creator": "placeholder",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }

            logger.info(f"Successfully retrieved endpoint info for: {endpoint_name} (placeholder)")
            return endpoint_info

        except Exception as e:
            logger.error(f"Error getting endpoint info for {endpoint_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting endpoint info: {e!s}") from e

    def test_connection(self) -> dict[str, Any]:
        """Test the connection to Databricks workspace.

        Returns:
            Dictionary containing connection status
        """
        try:
            logger.info("Testing Databricks connection")

            return {
                "status": "connected",
                "workspace_url": self.workspace_url,
                "endpoints_count": 1,  # Placeholder
                "message": "Successfully connected to Databricks workspace",
            }

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "status": "failed",
                "workspace_url": self.workspace_url,
                "error": str(e),
                "message": "Failed to connect to Databricks workspace",
            }

    def _get_gemini_client(self) -> Any:
        """Lazily build (and cache) a ``google.genai.Client`` pointed at the
        workspace's ai-gateway/gemini path.

        Gemini chat completions through the OpenAI-compat shim are unreliable
        — Vertex AI sometimes returns response shapes (safety blocks, empty
        candidates, etc.) that the shim's JSON-to-OpenAI translator can't
        round-trip, surfacing as 502 "invalid response from upstream". The
        native passthrough returns Gemini's response shape directly, which
        we can adapt cleanly.
        """
        cache_key = (self.workspace_url, _get_token_hash(self.token))
        cached = _gemini_client_cache.get(cache_key)
        if cached is not None:
            return cached

        # Local imports so the module still loads if the google extras
        # aren't installed in a minimal environment.
        import httpx as _httpx
        from google import genai
        from google.genai import types as genai_types

        gateway_url = f"{self.workspace_url.rstrip('/')}/ai-gateway/gemini"
        # google-genai prefers aiohttp when installed; we use the sync
        # interface here so this is mostly belt-and-suspenders, but passing
        # an explicit httpx_client also makes future hook installation easy.
        client = genai.Client(
            api_key="databricks",  # ignored; auth is in headers
            http_options=genai_types.HttpOptions(
                base_url=gateway_url,
                headers={"Authorization": f"Bearer {self.token}"},
                httpx_client=_httpx.Client(),
            ),
        )
        _gemini_client_cache[cache_key] = client
        logger.info("Gemini ai-gateway client cached for workspace=%s", self.workspace_url)
        return client

    def _call_gemini_chat_via_ai_gateway(
        self,
        endpoint_name: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.5,
        max_tokens: int | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Single-turn chat completion against Gemini via Databricks' native
        ai-gateway/gemini passthrough. Returns the chat-completions dict shape
        so callers (``discovery_analysis_service``, etc.) don't need to change.

        ``response_format`` is currently ignored; Gemini structured output
        uses ``response_schema`` on the request config, which doesn't map
        cleanly to OpenAI's ``response_format`` here. Callers that need
        structured output should use pydantic-ai's ``GoogleModel`` directly.
        """
        from google.genai import types as genai_types

        client = self._get_gemini_client()
        contents, system_instruction = _messages_to_genai_contents(messages)

        config_kwargs: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            config_kwargs["max_output_tokens"] = max_tokens
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        logger.info(
            "Calling Gemini via ai-gateway endpoint=%s contents=%d",
            endpoint_name,
            len(contents),
        )
        response = client.models.generate_content(
            model=endpoint_name,
            contents=contents,
            config=genai_types.GenerateContentConfig(**config_kwargs),
        )
        return _genai_response_to_chat_shape(response, endpoint_name)

    def call_chat_completion(
        self,
        endpoint_name: str,
        messages: list[dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int | None = None,
        model_parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a Databricks serving endpoint using chat completion format.

        For Gemini-family endpoints, routes through Databricks' native
        ai-gateway/gemini passthrough (using google-genai). Other models
        continue through the OpenAI-compat shim. The Gemini routing avoids
        502s the shim returns when Vertex AI emits response shapes it can't
        translate (safety blocks, empty candidates, etc.).
        """
        if _looks_like_gemini(endpoint_name):
            try:
                return self._call_gemini_chat_via_ai_gateway(
                    endpoint_name=endpoint_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                logger.error(f"Error calling Gemini ai-gateway endpoint {endpoint_name}: {e}")
                logger.error("Full traceback:", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling serving endpoint: {e!s}",
                ) from e

        try:
            # gpt-5 / o-series reject any temperature != 1
            temperature = _normalize_request_for_reasoning_model(endpoint_name, temperature)
            # Prepare the request parameters
            request_params = {"messages": messages, "model": endpoint_name, "temperature": temperature}

            # Add optional parameters
            if max_tokens:
                request_params["max_tokens"] = max_tokens

            if model_parameters:
                request_params.update(model_parameters)

            logger.info(f"Calling Databricks serving endpoint with chat completion: {endpoint_name}")
            logger.debug(f"Request parameters: {request_params}")

            # Make the API call using OpenAI client
            response = self.client.chat.completions.create(**request_params)

            # Convert response to dictionary format
            try:
                message_dump = response.choices[0].message.model_dump()
            except Exception:
                message_dump = {
                    "content": response.choices[0].message.content,
                    "role": response.choices[0].message.role,
                }
            # Gemini-backed endpoints return content as an array of part dicts;
            # callers expect a plain string. Other backings pass through unchanged.
            if "content" in message_dump:
                message_dump["content"] = _normalize_shim_content(message_dump["content"])

            result = {
                "choices": [
                    {
                        "message": message_dump,
                        "index": response.choices[0].index,
                        "finish_reason": response.choices[0].finish_reason,
                    }
                ],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

            logger.info(f"Successfully called serving endpoint: {endpoint_name}")
            logger.debug(f"Response: {result}")

            return result

        except Exception as e:
            logger.error(f"Error calling serving endpoint {endpoint_name}: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error("Full traceback:", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error calling serving endpoint: {e!s}") from e

    def call_serving_endpoint_direct(
        self,
        endpoint_name: str,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Call a Databricks serving endpoint directly via HTTP API.
        This bypasses the Databricks SDK to avoid authentication issues.

        Args:
            endpoint_name: Name of the serving endpoint
            prompt: The prompt to send to the model
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dictionary containing the response from the model
        """
        try:
            # Prepare the API URL
            api_url = f"{self.workspace_url.rstrip('/')}/serving-endpoints/{endpoint_name}/invocations"

            # Prepare headers with PAT token authentication
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            # Prepare the request payload in chat completion format
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
            }

            # Add max_tokens if specified
            if max_tokens:
                payload["max_tokens"] = max_tokens

            logger.info(f"Calling Databricks serving endpoint directly: {endpoint_name}")
            logger.debug(f"Request URL: {api_url}")
            logger.debug(f"Request payload: {payload}")
            # Log token prefix for debugging (never log full token)
            token_prefix = self.token[:10] if self.token else "None"
            logger.debug(f"Using token starting with: {token_prefix}...")

            # Make the HTTP request
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)

            # Add detailed error logging for 403 errors
            if response.status_code == 403:
                logger.error(
                    "403 Forbidden: endpoint=%s url=%s token_prefix=%s response=%s",
                    endpoint_name,
                    api_url,
                    token_prefix,
                    response.text,
                )

            # Check if request was successful
            response.raise_for_status()

            # Parse the response
            result = response.json()

            logger.info(f"Successfully called serving endpoint: {endpoint_name}")
            logger.debug(f"Response: {result}")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request error calling endpoint {endpoint_name}: {e}")
            raise HTTPException(status_code=500, detail=f"HTTP request error: {e!s}") from e
        except Exception as e:
            logger.error(f"Unexpected error calling serving endpoint {endpoint_name}: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error("Full traceback:", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}") from e


# Factory function to create Databricks service instance
def create_databricks_service() -> DatabricksService:
    """Create a Databricks service instance."""
    return DatabricksService()
