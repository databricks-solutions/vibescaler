# VibeScaler (Human Evaluation Workshop)

Copyright (2026) Databricks, Inc.

This Software includes software developed at Databricks (https://www.databricks.com/) and its use is subject to the included [LICENSE.md](LICENSE.md) file.

---

Third-party dependencies are grouped below by license. Each table row lists a package used by this project, along with its version, ecosystem, role (runtime or dev), copyright holder/author, and upstream source.

This inventory was generated from real package metadata: `pip-licenses` (run via `uv run --with pip-licenses`) against the project virtual environment for Python packages (direct and transitive), `uv export --no-dev` to distinguish runtime from dev Python dependencies, and the `license`, `author`, and `repository` fields of each installed `node_modules/<package>/package.json` for the direct Node dependencies declared in `client/package.json` and `docs/package.json`.

A few packages listed in `uv.lock` are platform-conditional and not installed in this environment (e.g. `colorama`, `pywin32`, `tomli`, `waitress`, `greenlet`, `prettytable`, `wcwidth`); they are not inventoried here.

**Dual-licensed and multi-licensed packages** — the following packages declare more than one license. Each is listed once below, under the license noted:

- `aiohttp` — Apache-2.0 **AND** MIT (combined work; listed under Apache License 2.0)
- `cryptography` — Apache-2.0 **OR** BSD-3-Clause (listed under Apache License 2.0)
- `numpy` — BSD-3-Clause **AND** 0BSD **AND** MIT **AND** Zlib **AND** CC0-1.0 (combined work; listed under BSD 3-Clause License)
- `orjson` — MPL-2.0 **AND** (Apache-2.0 **OR** MIT) (listed under Mozilla Public License 2.0)
- `packaging` — Apache-2.0 **OR** BSD-2-Clause (listed under Apache License 2.0)
- `python-dateutil` — Apache-2.0 **OR** BSD-3-Clause (listed under Apache License 2.0)
- `regex` — Apache-2.0 **AND** CNRI-Python (combined work; listed under Apache License 2.0)
- `sniffio` — Apache-2.0 **OR** MIT (listed under Apache License 2.0)
- `tqdm` — MPL-2.0 **AND** MIT (combined work; listed under Mozilla Public License 2.0)
- `uvloop` — Apache-2.0 **OR** MIT (listed under Apache License 2.0)

---

## Apache License 2.0

Full license text: [https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| @playwright/test | 1.60.0 | Node (client) | dev | Microsoft Corporation | [https://github.com/microsoft/playwright](https://github.com/microsoft/playwright) |
| aiohttp | 3.13.3 | Python | runtime | — | [https://github.com/aio-libs/aiohttp](https://github.com/aio-libs/aiohttp) |
| aiosignal | 1.4.0 | Python | runtime | — | [https://github.com/aio-libs/aiosignal](https://github.com/aio-libs/aiosignal) |
| asttokens | 3.0.1 | Python | dev | Dmitry Sagalovskiy, Grist Labs | [https://github.com/gristlabs/asttokens](https://github.com/gristlabs/asttokens) |
| bcrypt | 5.0.0 | Python | runtime | The Python Cryptographic Authority developers | [https://github.com/pyca/bcrypt/](https://github.com/pyca/bcrypt/) |
| boto3 | 1.42.53 | Python | runtime | Amazon Web Services | [https://github.com/boto/boto3](https://github.com/boto/boto3) |
| botocore | 1.42.53 | Python | runtime | Amazon Web Services | [https://github.com/boto/botocore](https://github.com/boto/botocore) |
| class-variance-authority | 0.7.1 | Node (client) | runtime | Joe Bell (https://joebell.co.uk) | [https://github.com/joe-bell/cva](https://github.com/joe-bell/cva) |
| coverage | 7.13.4 | Python | dev | Ned Batchelder and 252 others | [https://github.com/coveragepy/coveragepy](https://github.com/coveragepy/coveragepy) |
| cryptography | 46.0.5 | Python | runtime | The Python Cryptographic Authority and individual contributors | [https://github.com/pyca/cryptography](https://github.com/pyca/cryptography) |
| databricks-sdk | 0.91.0 | Python | runtime | — | [https://databricks-sdk-py.readthedocs.io](https://databricks-sdk-py.readthedocs.io) |
| databricks-sql-connector | 4.2.5 | Python | runtime | Databricks | [https://github.com/databricks/databricks-sql-python](https://github.com/databricks/databricks-sql-python) |
| diskcache | 5.6.3 | Python | runtime | Grant Jenks | [http://www.grantjenks.com/docs/diskcache/](http://www.grantjenks.com/docs/diskcache/) |
| distro | 1.9.0 | Python | runtime | Nir Cohen | [https://github.com/python-distro/distro](https://github.com/python-distro/distro) |
| docker | 7.1.0 | Python | runtime | — | [https://github.com/docker/docker-py](https://github.com/docker/docker-py) |
| frozenlist | 1.8.0 | Python | runtime | — | [https://github.com/aio-libs/frozenlist](https://github.com/aio-libs/frozenlist) |
| google-api-core | 2.30.0 | Python | runtime | Google LLC | [https://github.com/googleapis/google-cloud-python/tree/main/packages/google-api-core](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-api-core) |
| google-auth | 2.53.0 | Python | runtime | Google Cloud Platform | [https://github.com/googleapis/google-auth-library-python](https://github.com/googleapis/google-auth-library-python) |
| google-cloud-core | 2.5.0 | Python | runtime | Google LLC | [https://github.com/googleapis/python-cloud-core](https://github.com/googleapis/python-cloud-core) |
| google-cloud-storage | 3.9.0 | Python | runtime | Google LLC | [https://github.com/googleapis/python-storage](https://github.com/googleapis/python-storage) |
| google-genai | 2.4.0 | Python | runtime | Google LLC | [https://github.com/googleapis/python-genai](https://github.com/googleapis/python-genai) |
| google-resumable-media | 2.8.0 | Python | runtime | Google Cloud Platform | [https://github.com/googleapis/google-resumable-media-python](https://github.com/googleapis/google-resumable-media-python) |
| googleapis-common-protos | 1.72.0 | Python | runtime | Google LLC | [https://github.com/googleapis/google-cloud-python/tree/main/packages/googleapis-common-protos](https://github.com/googleapis/google-cloud-python/tree/main/packages/googleapis-common-protos) |
| hf-xet | 1.2.0 | Python | runtime | — | [https://github.com/huggingface/xet-core](https://github.com/huggingface/xet-core) |
| huggingface_hub | 1.4.1 | Python | runtime | Hugging Face, Inc. | [https://github.com/huggingface/huggingface_hub](https://github.com/huggingface/huggingface_hub) |
| importlib_metadata | 8.7.1 | Python | runtime | Jason R. Coombs | [https://github.com/python/importlib_metadata](https://github.com/python/importlib_metadata) |
| jsonpath-ng | 1.7.0 | Python | runtime | Tomas Aparicio | [https://github.com/h2non/jsonpath-ng](https://github.com/h2non/jsonpath-ng) |
| mlflow | 3.10.0 | Python | runtime | — | [https://mlflow.org](https://mlflow.org) |
| mlflow-skinny | 3.10.0 | Python | runtime | — | [https://mlflow.org](https://mlflow.org) |
| mlflow-tracing | 3.10.0 | Python | runtime | — | [https://mlflow.org](https://mlflow.org) |
| multidict | 6.7.1 | Python | runtime | Andrew Svetlov | [https://github.com/aio-libs/multidict](https://github.com/aio-libs/multidict) |
| openai | 2.30.0 | Python | runtime | OpenAI | [https://github.com/openai/openai-python](https://github.com/openai/openai-python) |
| opentelemetry-api | 1.39.1 | Python | runtime | OpenTelemetry Authors | [https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-api](https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-api) |
| opentelemetry-proto | 1.39.1 | Python | runtime | OpenTelemetry Authors | [https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-proto](https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-proto) |
| opentelemetry-sdk | 1.39.1 | Python | runtime | OpenTelemetry Authors | [https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-sdk](https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-sdk) |
| opentelemetry-semantic-conventions | 0.60b1 | Python | runtime | OpenTelemetry Authors | [https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-semantic-conventions](https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-semantic-conventions) |
| packaging | 26.0 | Python | runtime | Donald Stufft | [https://github.com/pypa/packaging](https://github.com/pypa/packaging) |
| propcache | 0.4.1 | Python | runtime | Andrew Svetlov | [https://github.com/aio-libs/propcache](https://github.com/aio-libs/propcache) |
| proto-plus | 1.27.1 | Python | runtime | Google LLC | [https://github.com/googleapis/proto-plus-python](https://github.com/googleapis/proto-plus-python) |
| pyarrow | 23.0.1 | Python | runtime | — | [https://arrow.apache.org/](https://arrow.apache.org/) |
| pytest-asyncio | 1.3.0 | Python | dev | Tin Tvrtković | [https://github.com/pytest-dev/pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) |
| python-dateutil | 2.9.0.post0 | Python | runtime | Gustavo Niemeyer | [https://github.com/dateutil/dateutil](https://github.com/dateutil/dateutil) |
| python-multipart | 0.0.22 | Python | runtime | Andrew Dunham, Marcelo Trylesinski | [https://github.com/Kludex/python-multipart](https://github.com/Kludex/python-multipart) |
| regex | 2026.2.19 | Python | runtime | Matthew Barnett | [https://github.com/mrabarnett/mrab-regex](https://github.com/mrabarnett/mrab-regex) |
| requests | 2.32.5 | Python | runtime | Kenneth Reitz | [https://requests.readthedocs.io](https://requests.readthedocs.io) |
| requests-toolbelt | 1.0.0 | Python | runtime | Ian Cordasco, Cory Benfield | [https://toolbelt.readthedocs.io/](https://toolbelt.readthedocs.io/) |
| s3transfer | 0.16.0 | Python | runtime | Amazon Web Services | [https://github.com/boto/s3transfer](https://github.com/boto/s3transfer) |
| sniffio | 1.3.1 | Python | runtime | Nathaniel J. Smith | [https://github.com/python-trio/sniffio](https://github.com/python-trio/sniffio) |
| tenacity | 9.1.4 | Python | runtime | Julien Danjou | [https://github.com/jd/tenacity](https://github.com/jd/tenacity) |
| testcontainers | 4.14.1 | Python | dev | Sergey Pirogov | — |
| thrift | 0.20.0 | Python | runtime | Apache Thrift Developers | [http://thrift.apache.org](http://thrift.apache.org) |
| tokenizers | 0.22.2 | Python | runtime | Nicolas Patry, Anthony Moi | [https://github.com/huggingface/tokenizers](https://github.com/huggingface/tokenizers) |
| tornado | 6.5.4 | Python | dev | Facebook | [http://www.tornadoweb.org/](http://www.tornadoweb.org/) |
| typescript | 5.9.3 | Node (client) | runtime | Microsoft Corp. | [https://github.com/microsoft/TypeScript](https://github.com/microsoft/TypeScript) |
| tzdata | 2025.3 | Python | runtime | Python Software Foundation | [https://github.com/python/tzdata](https://github.com/python/tzdata) |
| uvloop | 0.22.1 | Python | runtime | Yury Selivanov | — |
| yarl | 1.22.0 | Python | runtime | Andrew Svetlov | [https://github.com/aio-libs/yarl](https://github.com/aio-libs/yarl) |

---

## BSD 2-Clause License

Full license text: [https://opensource.org/licenses/BSD-2-Clause](https://opensource.org/licenses/BSD-2-Clause).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| @typescript-eslint/parser | 6.21.0 | Node (client) | dev | — | [https://github.com/typescript-eslint/typescript-eslint](https://github.com/typescript-eslint/typescript-eslint) |
| pyasn1 | 0.6.2 | Python | runtime | Ilya Etingof | [https://github.com/pyasn1/pyasn1](https://github.com/pyasn1/pyasn1) |
| terser | 5.48.0 | Node (client) | runtime | Mihai Bazon (http://lisperator.net/) | [https://github.com/terser/terser](https://github.com/terser/terser) |
| wrapt | 2.1.1 | Python | runtime | Graham Dumpleton | [https://github.com/GrahamDumpleton/wrapt](https://github.com/GrahamDumpleton/wrapt) |

---

## BSD 3-Clause License

Full license text: [https://opensource.org/licenses/BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| click | 8.3.1 | Python | runtime | — | [https://github.com/pallets/click/](https://github.com/pallets/click/) |
| Flask | 3.1.3 | Python | runtime | — | [https://github.com/pallets/flask/](https://github.com/pallets/flask/) |
| fsspec | 2026.2.0 | Python | runtime | — | [https://github.com/fsspec/filesystem_spec](https://github.com/fsspec/filesystem_spec) |
| GitPython | 3.1.46 | Python | runtime | Sebastian Thiel, Michael Trier | [https://github.com/gitpython-developers/GitPython](https://github.com/gitpython-developers/GitPython) |
| httpcore | 1.0.9 | Python | runtime | Tom Christie | [https://www.encode.io/httpcore/](https://www.encode.io/httpcore/) |
| idna | 3.11 | Python | runtime | Kim Davies | [https://github.com/kjd/idna](https://github.com/kjd/idna) |
| ipykernel | 7.2.0 | Python | dev | IPython Development Team | [https://ipython.org](https://ipython.org) |
| ipython | 9.10.0 | Python | dev | The IPython Development Team | [https://ipython.org](https://ipython.org) |
| joblib | 1.5.3 | Python | runtime | Gael Varoquaux | [https://joblib.readthedocs.io](https://joblib.readthedocs.io) |
| jupyter_core | 5.9.1 | Python | dev | Jupyter Development Team | [https://jupyter.org](https://jupyter.org) |
| MarkupSafe | 3.0.3 | Python | runtime | — | [https://github.com/pallets/markupsafe/](https://github.com/pallets/markupsafe/) |
| numpy | 2.4.2 | Python | runtime | Travis E. Oliphant et al. | [https://numpy.org](https://numpy.org) |
| oauthlib | 3.3.1 | Python | runtime | The OAuthlib Community | [https://github.com/oauthlib/oauthlib](https://github.com/oauthlib/oauthlib) |
| protobuf | 6.33.5 | Python | runtime | protobuf@googlegroups.com | [https://developers.google.com/protocol-buffers/](https://developers.google.com/protocol-buffers/) |
| psutil | 7.2.2 | Python | dev | Giampaolo Rodola | [https://github.com/giampaolo/psutil](https://github.com/giampaolo/psutil) |
| pycparser | 3.0 | Python | runtime | Eli Bendersky | [https://github.com/eliben/pycparser](https://github.com/eliben/pycparser) |
| python-dotenv | 1.2.1 | Python | runtime | Saurabh Kumar | [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) |
| scikit-learn | 1.8.0 | Python | runtime | — | [https://scikit-learn.org](https://scikit-learn.org) |
| starlette | 0.52.1 | Python | runtime | Tom Christie | [https://github.com/Kludex/starlette](https://github.com/Kludex/starlette) |
| uvicorn | 0.41.0 | Python | runtime | Tom Christie | [https://uvicorn.dev/](https://uvicorn.dev/) |
| websockets | 16.0 | Python | runtime | Aymeric Augustin | [https://github.com/python-websockets/websockets](https://github.com/python-websockets/websockets) |
| Werkzeug | 3.1.6 | Python | runtime | — | [https://github.com/pallets/werkzeug/](https://github.com/pallets/werkzeug/) |
| zstandard | 0.25.0 | Python | runtime | Gregory Szorc | [https://github.com/indygreg/python-zstandard](https://github.com/indygreg/python-zstandard) |

---

## BSD License (variant unspecified in metadata)

Full license text: [https://opensource.org/licenses/BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| appnope | 0.1.4 | Python | dev | Min Ragan-Kelley | [http://github.com/minrk/appnope](http://github.com/minrk/appnope) |
| asgiref | 3.11.1 | Python | runtime | Django Software Foundation | [https://github.com/django/asgiref/](https://github.com/django/asgiref/) |
| cloudpickle | 3.1.2 | Python | runtime | The cloudpickle developer team | [https://github.com/cloudpipe/cloudpickle](https://github.com/cloudpipe/cloudpickle) |
| comm | 0.2.3 | Python | dev | Jupyter contributors | [https://github.com/ipython/comm](https://github.com/ipython/comm) |
| contourpy | 1.3.3 | Python | runtime | Ian Thomas | [https://github.com/contourpy/contourpy](https://github.com/contourpy/contourpy) |
| cycler | 0.12.1 | Python | runtime | Thomas A Caswell | [https://matplotlib.org/cycler/](https://matplotlib.org/cycler/) |
| decorator | 5.2.1 | Python | dev | Michele Simionato | — |
| fastuuid | 0.14.0 | Python | runtime | — | [https://github.com/thedrow/fastuuid/](https://github.com/thedrow/fastuuid/) |
| gitdb | 4.0.12 | Python | runtime | Sebastian Thiel | [https://github.com/gitpython-developers/gitdb](https://github.com/gitpython-developers/gitdb) |
| httpx | 0.28.1 | Python | runtime | Tom Christie | [https://github.com/encode/httpx](https://github.com/encode/httpx) |
| ipython_pygments_lexers | 1.1.1 | Python | dev | The IPython Development Team | [https://github.com/ipython/ipython-pygments-lexers](https://github.com/ipython/ipython-pygments-lexers) |
| isodate | 0.7.2 | Python | runtime | Gerhard Weis | [https://github.com/gweis/isodate/](https://github.com/gweis/isodate/) |
| itsdangerous | 2.2.0 | Python | runtime | — | [https://github.com/pallets/itsdangerous/](https://github.com/pallets/itsdangerous/) |
| Jinja2 | 3.1.6 | Python | runtime | — | [https://github.com/pallets/jinja/](https://github.com/pallets/jinja/) |
| jsonpatch | 1.33 | Python | runtime | Stefan Kögl | [https://github.com/stefankoegl/python-json-patch](https://github.com/stefankoegl/python-json-patch) |
| jsonpointer | 3.0.0 | Python | runtime | Stefan Kögl | [https://github.com/stefankoegl/python-json-pointer](https://github.com/stefankoegl/python-json-pointer) |
| jupyter_client | 8.8.0 | Python | dev | Jupyter Development Team | [https://jupyter.org](https://jupyter.org) |
| kiwisolver | 1.4.9 | Python | runtime | The Nucleic Development Team | [https://github.com/nucleic/kiwi](https://github.com/nucleic/kiwi) |
| lz4 | 4.4.5 | Python | runtime | Jonathan Underwood | [https://github.com/python-lz4/python-lz4](https://github.com/python-lz4/python-lz4) |
| nest-asyncio | 1.6.0 | Python | dev | Ewald R. de Wit | [https://github.com/erdewit/nest_asyncio](https://github.com/erdewit/nest_asyncio) |
| nodeenv | 1.10.0 | Python | dev | Eugene Kalinin | [https://github.com/ekalinin/nodeenv](https://github.com/ekalinin/nodeenv) |
| pandas | 2.3.3 | Python | runtime | The Pandas Development Team | [https://pandas.pydata.org](https://pandas.pydata.org) |
| ply | 3.11 | Python | runtime | David Beazley | [http://www.dabeaz.com/ply/](http://www.dabeaz.com/ply/) |
| prompt_toolkit | 3.0.52 | Python | dev | Jonathan Slenders | [https://github.com/prompt-toolkit/python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) |
| pyasn1_modules | 0.4.2 | Python | runtime | Ilya Etingof | [https://github.com/pyasn1/pyasn1-modules](https://github.com/pyasn1/pyasn1-modules) |
| pybreaker | 1.4.1 | Python | runtime | Daniel Fernandes Martins | [http://github.com/danielfm/pybreaker](http://github.com/danielfm/pybreaker) |
| Pygments | 2.19.2 | Python | runtime | Georg Brandl | [https://pygments.org](https://pygments.org) |
| pyzmq | 27.1.0 | Python | dev | Brian E. Granger, Min Ragan-Kelley | [https://pyzmq.readthedocs.org](https://pyzmq.readthedocs.org) |
| scipy | 1.17.0 | Python | runtime | — | [https://scipy.org/](https://scipy.org/) |
| smmap | 5.0.2 | Python | runtime | Sebastian Thiel | [https://github.com/gitpython-developers/smmap](https://github.com/gitpython-developers/smmap) |
| sqlparse | 0.5.5 | Python | runtime | Andi Albrecht | [https://github.com/andialbrecht/sqlparse](https://github.com/andialbrecht/sqlparse) |
| threadpoolctl | 3.6.0 | Python | runtime | Thomas Moreau | [https://github.com/joblib/threadpoolctl](https://github.com/joblib/threadpoolctl) |
| traitlets | 5.14.3 | Python | dev | IPython Development Team | [https://github.com/ipython/traitlets](https://github.com/ipython/traitlets) |
| uuid_utils | 0.14.0 | Python | runtime | Amin Alaee | [https://github.com/aminalaee/uuid-utils](https://github.com/aminalaee/uuid-utils) |
| xxhash | 3.6.0 | Python | runtime | Yue Du | [https://github.com/ifduyue/python-xxhash](https://github.com/ifduyue/python-xxhash) |

---

## ISC License

Full license text: [https://opensource.org/licenses/ISC](https://opensource.org/licenses/ISC).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| glob | 10.5.0 | Node (client) | dev | Isaac Z. Schlueter (https://blog.izs.me/) | [https://github.com/isaacs/node-glob](https://github.com/isaacs/node-glob) |
| griffelib | 2.0.2 | Python | runtime | Timothée Mazzucotelli | — |
| knip | 5.88.1 | Node (client) | dev | Lars Kappert | [https://github.com/webpro-nl/knip](https://github.com/webpro-nl/knip) |
| lucide-react | 0.525.0 | Node (client) | runtime | Eric Fennis | [https://github.com/lucide-icons/lucide](https://github.com/lucide-icons/lucide) |
| pexpect | 4.9.0 | Python | dev | Noah Spurrier; Thomas Kluyver; Jeff Quast | [https://pexpect.readthedocs.io/](https://pexpect.readthedocs.io/) |
| ptyprocess | 0.7.0 | Python | dev | Thomas Kluyver | [https://github.com/pexpect/ptyprocess](https://github.com/pexpect/ptyprocess) |
| shellingham | 1.5.4 | Python | runtime | Tzu-ping Chung | [https://github.com/sarugaku/shellingham](https://github.com/sarugaku/shellingham) |

---

## GNU Lesser General Public License v3.0 (LGPL-3.0-only)

Full license text: [https://www.gnu.org/licenses/lgpl-3.0.html](https://www.gnu.org/licenses/lgpl-3.0.html).

The `psycopg` family is used as an unmodified PostgreSQL driver dependency (dynamic linking / import only; no modifications are distributed).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| psycopg | 3.3.3 | Python | runtime | Daniele Varrazzo | [https://psycopg.org/](https://psycopg.org/) |
| psycopg-binary | 3.3.3 | Python | runtime | Daniele Varrazzo | [https://psycopg.org/](https://psycopg.org/) |
| psycopg-pool | 3.3.0 | Python | runtime | Daniele Varrazzo | [https://psycopg.org/](https://psycopg.org/) |

---

## MIT License

Full license text: [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| @copilotkit/react-core | 1.59.2 | Node (client) | runtime | — | [https://github.com/CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) |
| @copilotkit/react-ui | 1.59.2 | Node (client) | runtime | — | [https://github.com/CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) |
| @docusaurus/core | 3.10.1 | Node (docs) | runtime | — | [https://github.com/facebook/docusaurus](https://github.com/facebook/docusaurus) |
| @docusaurus/preset-classic | 3.10.1 | Node (docs) | runtime | — | [https://github.com/facebook/docusaurus](https://github.com/facebook/docusaurus) |
| @easyops-cn/docusaurus-search-local | 0.55.2 | Node (docs) | runtime | — | [https://github.com/easyops-cn/docusaurus-search-local](https://github.com/easyops-cn/docusaurus-search-local) |
| @eslint/js | 8.57.1 | Node (client) | dev | — | [https://github.com/eslint/eslint](https://github.com/eslint/eslint) |
| @radix-ui/react-alert-dialog | 1.1.15 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-avatar | 1.1.11 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-dialog | 1.1.15 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-dropdown-menu | 2.1.16 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-icons | 1.3.2 | Node (client) | runtime | — | — |
| @radix-ui/react-label | 2.1.8 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-progress | 1.1.8 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-radio-group | 1.3.8 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-scroll-area | 1.2.10 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-select | 2.2.6 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-separator | 1.1.8 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-slot | 1.2.4 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-switch | 1.2.6 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @radix-ui/react-tabs | 1.1.13 | Node (client) | runtime | — | [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives) |
| @tailwindcss/typography | 0.5.19 | Node (client) | runtime | — | [https://github.com/tailwindlabs/tailwindcss-typography](https://github.com/tailwindlabs/tailwindcss-typography) |
| @tanstack/eslint-plugin-query | 5.101.0 | Node (client) | dev | Eliya Cohen | [https://github.com/TanStack/query](https://github.com/TanStack/query) |
| @tanstack/react-query | 5.101.0 | Node (client) | runtime | tannerlinsley | [https://github.com/TanStack/query](https://github.com/TanStack/query) |
| @testing-library/jest-dom | 6.9.1 | Node (client) | dev | Ernesto Garcia (http://gnapse.github.io) | [https://github.com/testing-library/jest-dom](https://github.com/testing-library/jest-dom) |
| @testing-library/react | 16.3.2 | Node (client) | dev | Kent C. Dodds (https://kentcdodds.com) | [https://github.com/testing-library/react-testing-library](https://github.com/testing-library/react-testing-library) |
| @testing-library/user-event | 14.6.1 | Node (client) | dev | Giorgio Polvara | [https://github.com/testing-library/user-event](https://github.com/testing-library/user-event) |
| @types/node | 25.9.1 | Node (client) | dev | Microsoft TypeScript | [https://github.com/DefinitelyTyped/DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) |
| @types/react | 18.3.30 | Node (client) | dev | Asana | [https://github.com/DefinitelyTyped/DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) |
| @types/react-dom | 18.3.7 | Node (client) | dev | Asana | [https://github.com/DefinitelyTyped/DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) |
| @typescript-eslint/eslint-plugin | 6.21.0 | Node (client) | dev | — | [https://github.com/typescript-eslint/typescript-eslint](https://github.com/typescript-eslint/typescript-eslint) |
| @vitejs/plugin-react-swc | 3.11.0 | Node (client) | runtime | Arnaud Barré (https://github.com/ArnaudBarre) | [https://github.com/vitejs/vite-plugin-react](https://github.com/vitejs/vite-plugin-react) |
| @vitest/coverage-v8 | 2.1.9 | Node (client) | dev | Anthony Fu | [https://github.com/vitest-dev/vitest](https://github.com/vitest-dev/vitest) |
| ag-ui-protocol | 0.1.19 | Python | runtime | Markus Ecker | — |
| alembic | 1.18.4 | Python | runtime | Mike Bayer | [https://alembic.sqlalchemy.org](https://alembic.sqlalchemy.org) |
| annotated-doc | 0.0.4 | Python | runtime | Sebastián Ramírez | [https://github.com/fastapi/annotated-doc](https://github.com/fastapi/annotated-doc) |
| annotated-types | 0.7.0 | Python | runtime | Adrian Garcia Badaracco, Samuel Colvin, Zac Hatfield-Dodds | [https://github.com/annotated-types/annotated-types](https://github.com/annotated-types/annotated-types) |
| anyio | 4.12.1 | Python | runtime | Alex Grönholm | [https://anyio.readthedocs.io/en/stable/versionhistory.html](https://anyio.readthedocs.io/en/stable/versionhistory.html) |
| asyncer | 0.0.8 | Python | runtime | Sebastián Ramírez | [https://github.com/fastapi/asyncer](https://github.com/fastapi/asyncer) |
| attrs | 25.4.0 | Python | runtime | Hynek Schlawack | [https://www.attrs.org/en/stable/changelog.html](https://www.attrs.org/en/stable/changelog.html) |
| autoprefixer | 10.5.0 | Node (client) | runtime | Andrey Sitnik | [https://github.com/postcss/autoprefixer](https://github.com/postcss/autoprefixer) |
| azure-core | 1.38.2 | Python | runtime | Microsoft Corporation | [https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core) |
| azure-storage-blob | 12.28.0 | Python | runtime | Microsoft Corporation | [https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob) |
| azure-storage-file-datalake | 12.23.0 | Python | runtime | Microsoft Corporation | [https://github.com/Azure/azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python) |
| black | 26.1.0 | Python | dev | Łukasz Langa | [https://github.com/psf/black](https://github.com/psf/black) |
| blinker | 1.9.0 | Python | runtime | Jason Kirtland | [https://github.com/pallets-eco/blinker/](https://github.com/pallets-eco/blinker/) |
| cachetools | 7.0.1 | Python | runtime | Thomas Kemmer | [https://github.com/tkem/cachetools/](https://github.com/tkem/cachetools/) |
| cffi | 2.0.0 | Python | runtime | Armin Rigo, Maciej Fijalkowski | [https://cffi.readthedocs.io/en/latest/whatsnew.html](https://cffi.readthedocs.io/en/latest/whatsnew.html) |
| cfgv | 3.5.0 | Python | dev | Anthony Sottile | [https://github.com/asottile/cfgv](https://github.com/asottile/cfgv) |
| charset-normalizer | 3.4.4 | Python | runtime | Ahmed R. TAHRI | [https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md](https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md) |
| clsx | 2.1.1 | Node (client) | runtime | Luke Edwards | [https://github.com/lukeed/clsx](https://github.com/lukeed/clsx) |
| colorlog | 6.10.1 | Python | runtime | Sam Clements | [https://github.com/borntyping/python-colorlog](https://github.com/borntyping/python-colorlog) |
| concurrently | 9.2.1 | Node (client) | dev | Kimmo Brunfeldt | [https://github.com/open-cli-tools/concurrently](https://github.com/open-cli-tools/concurrently) |
| croniter | 6.2.2 | Python | runtime | Matsumoto Taichi, kiorky, Ash Berlin-Taylor, Jarek Potiuk | [https://github.com/pallets-eco/croniter](https://github.com/pallets-eco/croniter) |
| dataclasses-json | 0.6.7 | Python | runtime | Charles Li | [https://github.com/lidatong/dataclasses-json](https://github.com/lidatong/dataclasses-json) |
| debugpy | 1.8.20 | Python | dev | Microsoft Corporation | [https://aka.ms/debugpy](https://aka.ms/debugpy) |
| Deprecated | 1.3.1 | Python | runtime | Laurent LAPORTE | [https://github.com/laurent-laporte-pro/deprecated](https://github.com/laurent-laporte-pro/deprecated) |
| dspy | 3.1.3 | Python | runtime | Omar Khattab | [https://github.com/stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) |
| eslint | 8.57.1 | Node (client) | dev | Nicholas C. Zakas | [https://github.com/eslint/eslint](https://github.com/eslint/eslint) |
| eslint-plugin-react-hooks | 4.6.2 | Node (client) | dev | — | [https://github.com/facebook/react](https://github.com/facebook/react) |
| eslint-plugin-react-refresh | 0.4.26 | Node (client) | dev | Arnaud Barré (https://github.com/ArnaudBarre) | [https://github.com/ArnaudBarre/eslint-plugin-react-refresh](https://github.com/ArnaudBarre/eslint-plugin-react-refresh) |
| et_xmlfile | 2.0.0 | Python | runtime | See AUTHORS.txt | [https://foss.heptapod.net/openpyxl/et_xmlfile](https://foss.heptapod.net/openpyxl/et_xmlfile) |
| executing | 2.2.1 | Python | dev | Alex Hall | [https://github.com/alexmojaki/executing](https://github.com/alexmojaki/executing) |
| fastapi | 0.129.0 | Python | runtime | Sebastián Ramírez | [https://github.com/fastapi/fastapi](https://github.com/fastapi/fastapi) |
| filelock | 3.24.3 | Python | runtime | — | [https://github.com/tox-dev/py-filelock](https://github.com/tox-dev/py-filelock) |
| flask-cors | 6.0.2 | Python | runtime | Cory Dolphin | [https://corydolphin.github.io/flask-cors/](https://corydolphin.github.io/flask-cors/) |
| fonttools | 4.61.1 | Python | runtime | Just van Rossum | [http://github.com/fonttools/fonttools](http://github.com/fonttools/fonttools) |
| genai-prices | 0.0.56 | Python | runtime | Samuel Colvin | [https://github.com/pydantic/genai-prices](https://github.com/pydantic/genai-prices) |
| gepa | 0.0.26 | Python | runtime | Lakshya A Agrawal | [https://github.com/gepa-ai/gepa](https://github.com/gepa-ai/gepa) |
| globals | 13.24.0 | Node (client) | dev | Sindre Sorhus | [https://github.com/sindresorhus/globals](https://github.com/sindresorhus/globals) |
| graphene | 3.4.3 | Python | runtime | Syrus Akbary | [https://github.com/graphql-python/graphene](https://github.com/graphql-python/graphene) |
| graphql-core | 3.2.7 | Python | runtime | Christoph Zwerschke | [https://github.com/graphql-python/graphql-core](https://github.com/graphql-python/graphql-core) |
| graphql-relay | 3.2.0 | Python | runtime | Syrus Akbary | [https://github.com/graphql-python/graphql-relay-py](https://github.com/graphql-python/graphql-relay-py) |
| gunicorn | 25.1.0 | Python | runtime | Benoit Chesneau | [https://gunicorn.org](https://gunicorn.org) |
| h11 | 0.16.0 | Python | runtime | Nathaniel J. Smith | [https://github.com/python-hyper/h11](https://github.com/python-hyper/h11) |
| httptools | 0.7.1 | Python | runtime | Yury Selivanov | [https://github.com/MagicStack/httptools](https://github.com/MagicStack/httptools) |
| huey | 2.6.0 | Python | runtime | Charles Leifer | [https://github.com/coleifer/huey](https://github.com/coleifer/huey) |
| identify | 2.6.16 | Python | dev | Chris Kuehl | [https://github.com/pre-commit/identify](https://github.com/pre-commit/identify) |
| iniconfig | 2.3.0 | Python | dev | Ronny Pfannschmidt, Holger Krekel | [https://github.com/pytest-dev/iniconfig](https://github.com/pytest-dev/iniconfig) |
| jedi | 0.19.2 | Python | dev | David Halter | [https://github.com/davidhalter/jedi](https://github.com/davidhalter/jedi) |
| jiter | 0.13.0 | Python | runtime | Samuel Colvin | [https://github.com/pydantic/jiter/](https://github.com/pydantic/jiter/) |
| jmespath | 1.1.0 | Python | runtime | James Saryerwinnie | [https://github.com/jmespath/jmespath.py](https://github.com/jmespath/jmespath.py) |
| jsdom | 24.1.3 | Node (client) | dev | — | [https://github.com/jsdom/jsdom](https://github.com/jsdom/jsdom) |
| json_repair | 0.58.0 | Python | runtime | Stefano Baccianella | [https://github.com/mangiucugna/json_repair/](https://github.com/mangiucugna/json_repair/) |
| jsonpath-plus | 10.4.0 | Node (client) | runtime | Stefan Goessner | [https://github.com/s3u/JSONPath](https://github.com/s3u/JSONPath) |
| jsonschema | 4.26.0 | Python | runtime | Julian Berman | [https://github.com/python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema) |
| jsonschema-specifications | 2025.9.1 | Python | runtime | Julian Berman | [https://github.com/python-jsonschema/jsonschema-specifications](https://github.com/python-jsonschema/jsonschema-specifications) |
| langchain-core | 1.2.14 | Python | runtime | — | [https://docs.langchain.com/](https://docs.langchain.com/) |
| langchain-openai | 1.1.10 | Python | runtime | — | [https://docs.langchain.com/oss/python/integrations/providers/openai](https://docs.langchain.com/oss/python/integrations/providers/openai) |
| langsmith | 0.7.5 | Python | runtime | LangChain | [https://smith.langchain.com/](https://smith.langchain.com/) |
| librt | 0.8.1 | Python | dev | Jukka Lehtosalo, Ivan Levkivskyi | [https://github.com/mypyc/librt](https://github.com/mypyc/librt) |
| limits | 5.8.0 | Python | runtime | Ali-Akber Saifee | [https://limits.readthedocs.org](https://limits.readthedocs.org) |
| litellm | 1.81.13 | Python | runtime | BerriAI | [https://litellm.ai](https://litellm.ai) |
| logfire-api | 4.31.0 | Python | runtime | Pydantic Team, Samuel Colvin, Hasan Ramezani, Adrian Garcia Badaracco, David Montague, Marcelo Trylesinski, David Hewitt, Alex Hall | — |
| Mako | 1.3.10 | Python | runtime | Mike Bayer | [https://www.makotemplates.org/](https://www.makotemplates.org/) |
| markdown-it-py | 4.0.0 | Python | runtime | Chris Sewell | [https://github.com/executablebooks/markdown-it-py](https://github.com/executablebooks/markdown-it-py) |
| marshmallow | 3.26.2 | Python | runtime | Steven Loria | [https://github.com/marshmallow-code/marshmallow](https://github.com/marshmallow-code/marshmallow) |
| mdurl | 0.1.2 | Python | runtime | Taneli Hukkinen | [https://github.com/executablebooks/mdurl](https://github.com/executablebooks/mdurl) |
| mypy | 1.19.1 | Python | dev | Jukka Lehtosalo | [https://www.mypy-lang.org/](https://www.mypy-lang.org/) |
| mypy_extensions | 1.1.0 | Python | runtime | The mypy developers | [https://github.com/python/mypy_extensions](https://github.com/python/mypy_extensions) |
| openpyxl | 3.1.5 | Python | runtime | See AUTHORS | [https://openpyxl.readthedocs.io](https://openpyxl.readthedocs.io) |
| optuna | 4.7.0 | Python | runtime | Takuya Akiba | [https://optuna.org/](https://optuna.org/) |
| parso | 0.8.6 | Python | dev | David Halter | [https://github.com/davidhalter/parso](https://github.com/davidhalter/parso) |
| platformdirs | 4.9.2 | Python | dev | — | [https://github.com/tox-dev/platformdirs](https://github.com/tox-dev/platformdirs) |
| pluggy | 1.6.0 | Python | dev | Holger Krekel | — |
| postcss | 8.5.15 | Node (client) | runtime | Andrey Sitnik | [https://github.com/postcss/postcss](https://github.com/postcss/postcss) |
| pre_commit | 4.5.1 | Python | dev | Anthony Sottile | [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) |
| prettier | 3.8.3 | Node (client) | dev | James Long | [https://github.com/prettier/prettier](https://github.com/prettier/prettier) |
| procrastinate | 3.8.1 | Python | runtime | Eric Lemoine, Kai Schlamp | [https://procrastinate.readthedocs.io/](https://procrastinate.readthedocs.io/) |
| pure_eval | 0.2.3 | Python | dev | Alex Hall | [http://github.com/alexmojaki/pure_eval](http://github.com/alexmojaki/pure_eval) |
| pydantic | 2.12.5 | Python | runtime | Samuel Colvin, Eric Jolibois, Hasan Ramezani, Adrian Garcia Badaracco, Terrence Dorsey, David Montague, Serge Matveenko, Marcelo Trylesinski, Sydney Runkle, David Hewitt, Alex Hall, Victorien Plot, Douwe Maan | [https://github.com/pydantic/pydantic](https://github.com/pydantic/pydantic) |
| pydantic-ai-slim | 1.77.0 | Python | runtime | Samuel Colvin, Marcelo Trylesinski, David Montague, Alex Hall, Douwe Maan | [https://github.com/pydantic/pydantic-ai/tree/main/pydantic_ai_slim](https://github.com/pydantic/pydantic-ai/tree/main/pydantic_ai_slim) |
| pydantic-graph | 1.77.0 | Python | runtime | Samuel Colvin, Marcelo Trylesinski, David Montague, Alex Hall, Douwe Maan | [https://ai.pydantic.dev/graph/tree/main/pydantic_graph](https://ai.pydantic.dev/graph/tree/main/pydantic_graph) |
| pydantic_core | 2.41.5 | Python | runtime | Samuel Colvin, Adrian Garcia Badaracco, David Montague, David Hewitt, Sydney Runkle, Victorien Plot | [https://github.com/pydantic/pydantic-core](https://github.com/pydantic/pydantic-core) |
| PyJWT | 2.11.0 | Python | runtime | Jose Padilla | [https://github.com/jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) |
| pyparsing | 3.3.2 | Python | runtime | Paul McGuire | [https://github.com/pyparsing/pyparsing/](https://github.com/pyparsing/pyparsing/) |
| pytest | 9.0.2 | Python | dev | Holger Krekel, Bruno Oliveira, Ronny Pfannschmidt, Floris Bruynooghe, Brianna Laugher, Florian Bruhin, Others (See AUTHORS) | [https://docs.pytest.org/en/latest/](https://docs.pytest.org/en/latest/) |
| pytest-cov | 7.0.0 | Python | dev | Marc Schlaich | [https://pytest-cov.readthedocs.io/en/latest/changelog.html](https://pytest-cov.readthedocs.io/en/latest/changelog.html) |
| pytest-json-report | 1.5.0 | Python | dev | numirias | [https://github.com/numirias/pytest-json-report](https://github.com/numirias/pytest-json-report) |
| pytokens | 0.4.1 | Python | dev | Tushar Sadhwani | [https://github.com/tusharsadhwani/pytokens](https://github.com/tusharsadhwani/pytokens) |
| pytz | 2025.2 | Python | runtime | Stuart Bishop | [http://pythonhosted.org/pytz](http://pythonhosted.org/pytz) |
| PyYAML | 6.0.3 | Python | runtime | Kirill Simonov | [https://pyyaml.org/](https://pyyaml.org/) |
| react | 18.3.1 | Node (client) | runtime | — | [https://github.com/facebook/react](https://github.com/facebook/react) |
| react | 18.3.1 | Node (docs) | runtime | — | [https://github.com/facebook/react](https://github.com/facebook/react) |
| react-dom | 18.3.1 | Node (client) | runtime | — | [https://github.com/facebook/react](https://github.com/facebook/react) |
| react-dom | 18.3.1 | Node (docs) | runtime | — | [https://github.com/facebook/react](https://github.com/facebook/react) |
| react-markdown | 10.1.0 | Node (client) | runtime | Espen Hovlandsdal | [https://github.com/remarkjs/react-markdown](https://github.com/remarkjs/react-markdown) |
| react-router-dom | 7.16.0 | Node (client) | runtime | Remix Software | [https://github.com/remix-run/react-router](https://github.com/remix-run/react-router) |
| referencing | 0.37.0 | Python | runtime | Julian Berman | [https://github.com/python-jsonschema/referencing](https://github.com/python-jsonschema/referencing) |
| remark-gfm | 4.0.1 | Node (client) | runtime | Titus Wormer (https://wooorm.com) | [https://github.com/remarkjs/remark-gfm](https://github.com/remarkjs/remark-gfm) |
| rich | 14.3.3 | Python | runtime | Will McGugan | [https://github.com/Textualize/rich](https://github.com/Textualize/rich) |
| rpds-py | 0.30.0 | Python | runtime | Julian Berman | [https://github.com/crate-py/rpds](https://github.com/crate-py/rpds) |
| ruff | 0.15.2 | Python | dev | Astral Software Inc. | [https://docs.astral.sh/ruff](https://docs.astral.sh/ruff) |
| six | 1.17.0 | Python | runtime | Benjamin Peterson | [https://github.com/benjaminp/six](https://github.com/benjaminp/six) |
| skops | 0.13.0 | Python | runtime | — | [http://github.com/skops-dev/skops](http://github.com/skops-dev/skops) |
| slowapi | 0.1.9 | Python | runtime | Laurent Savaete | [https://github.com/laurents/slowapi](https://github.com/laurents/slowapi) |
| sonner | 2.0.7 | Node (client) | runtime | Emil Kowalski | [https://github.com/emilkowalski/sonner](https://github.com/emilkowalski/sonner) |
| SQLAlchemy | 2.0.46 | Python | runtime | Mike Bayer | [https://www.sqlalchemy.org](https://www.sqlalchemy.org) |
| stack-data | 0.6.3 | Python | dev | Alex Hall | [http://github.com/alexmojaki/stack_data](http://github.com/alexmojaki/stack_data) |
| tailwind-merge | 2.6.1 | Node (client) | runtime | Dany Castillo | [https://github.com/dcastil/tailwind-merge](https://github.com/dcastil/tailwind-merge) |
| tailwindcss | 3.4.19 | Node (client) | runtime | — | [https://github.com/tailwindlabs/tailwindcss.git#v3](https://github.com/tailwindlabs/tailwindcss.git#v3) |
| tailwindcss-animate | 1.0.7 | Node (client) | runtime | Jamie Kyle | — |
| tiktoken | 0.12.0 | Python | runtime | Shantanu Jain | [https://github.com/openai/tiktoken](https://github.com/openai/tiktoken) |
| typer | 0.24.0 | Python | runtime | Sebastián Ramírez | [https://github.com/fastapi/typer](https://github.com/fastapi/typer) |
| typer-slim | 0.24.0 | Python | runtime | Sebastián Ramírez | [https://github.com/fastapi/typer](https://github.com/fastapi/typer) |
| typescript-eslint | 8.60.1 | Node (client) | dev | — | [https://github.com/typescript-eslint/typescript-eslint](https://github.com/typescript-eslint/typescript-eslint) |
| typing-inspect | 0.9.0 | Python | runtime | Ivan Levkivskyi | [https://github.com/ilevkivskyi/typing_inspect](https://github.com/ilevkivskyi/typing_inspect) |
| typing-inspection | 0.4.2 | Python | runtime | Victorien Plot | [https://github.com/pydantic/typing-inspection](https://github.com/pydantic/typing-inspection) |
| urllib3 | 2.6.3 | Python | runtime | Andrey Petrov | [https://github.com/urllib3/urllib3/blob/main/CHANGES.rst](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst) |
| virtualenv | 20.38.0 | Python | dev | — | [https://github.com/pypa/virtualenv](https://github.com/pypa/virtualenv) |
| vite | 5.4.21 | Node (client) | runtime | Evan You | [https://github.com/vitejs/vite](https://github.com/vitejs/vite) |
| vitest | 2.1.9 | Node (client) | dev | Anthony Fu | [https://github.com/vitest-dev/vitest](https://github.com/vitest-dev/vitest) |
| vulture | 2.14 | Python | dev | Jendrik Seipp | [https://github.com/jendrikseipp/vulture](https://github.com/jendrikseipp/vulture) |
| watchfiles | 1.1.1 | Python | runtime | Samuel Colvin | [https://github.com/samuelcolvin/watchfiles](https://github.com/samuelcolvin/watchfiles) |
| whenever | 0.7.3 | Python | runtime | Arie Bovenberg | [https://github.com/ariebovenberg/whenever](https://github.com/ariebovenberg/whenever) |
| zipp | 3.23.0 | Python | runtime | Jason R. Coombs | [https://github.com/jaraco/zipp](https://github.com/jaraco/zipp) |
| zod | 4.4.3 | Node (client) | runtime | Colin McDonnell | [https://github.com/colinhacks/zod](https://github.com/colinhacks/zod) |

---

## MIT-CMU License

Full license text: [https://spdx.org/licenses/MIT-CMU.html](https://spdx.org/licenses/MIT-CMU.html).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| pillow | 12.1.1 | Python | runtime | Jeffrey A. Clark | [https://python-pillow.github.io](https://python-pillow.github.io) |

---

## Mozilla Public License 2.0

Full license text: [https://opensource.org/licenses/MPL-2.0](https://opensource.org/licenses/MPL-2.0).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| certifi | 2026.1.4 | Python | runtime | Kenneth Reitz | [https://github.com/certifi/python-certifi](https://github.com/certifi/python-certifi) |
| orjson | 3.11.7 | Python | runtime | — | [https://github.com/ijl/orjson](https://github.com/ijl/orjson) |
| pathspec | 1.0.4 | Python | dev | Caleb P. Burns | [https://python-path-specification.readthedocs.io/en/latest/index.html](https://python-path-specification.readthedocs.io/en/latest/index.html) |
| pytest-metadata | 3.1.1 | Python | dev | Dave Hunt, Jim Brannlund | [https://github.com/pytest-dev/pytest-metadata](https://github.com/pytest-dev/pytest-metadata) |
| tqdm | 4.67.3 | Python | runtime | — | [https://tqdm.github.io](https://tqdm.github.io) |

---

## Python Software Foundation License

Full license text: [https://docs.python.org/3/license.html](https://docs.python.org/3/license.html).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| aiohappyeyeballs | 2.6.1 | Python | runtime | J. Nick Koston | [https://github.com/aio-libs/aiohappyeyeballs](https://github.com/aio-libs/aiohappyeyeballs) |
| distlib | 0.4.0 | Python | dev | Vinay Sajip | [https://github.com/pypa/distlib](https://github.com/pypa/distlib) |
| matplotlib | 3.10.8 | Python | runtime | John D. Hunter, Michael Droettboom | [https://matplotlib.org](https://matplotlib.org) |
| typing_extensions | 4.15.0 | Python | runtime | Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee | [https://github.com/python/typing_extensions](https://github.com/python/typing_extensions) |

---

## Other / Proprietary License

`databricks-agents` is published by Databricks under the [Databricks License](https://www.databricks.com/legal/db-license).

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| databricks-agents | 1.9.3 | Python | runtime | Databricks | — |

---

## Unknown / needs review

The installed metadata for these packages does not declare a license. They are listed here for manual review rather than guessed.

| Package | Version | Ecosystem | Role | Copyright holder / author | Source |
| --- | --- | --- | --- | --- | --- |
| google-crc32c | 1.8.0 | Python | runtime | Google LLC | [https://github.com/googleapis/python-crc32c](https://github.com/googleapis/python-crc32c) |
| matplotlib-inline | 0.2.1 | Python | dev | IPython Development Team | [https://github.com/ipython/matplotlib-inline](https://github.com/ipython/matplotlib-inline) |

---

## Support
Databricks does not offer official support for Databricks Solutions and its repository.
For any issue with this assets or the demos installed, please open an issue using github and the team will have a look on a best effort basis.
