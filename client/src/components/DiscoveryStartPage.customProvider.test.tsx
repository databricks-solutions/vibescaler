// @spec CUSTOM_LLM_PROVIDER_SPEC
// @req Custom provider option appears in the Discovery model selector when configured and enabled
import { describe, expect, it, vi, beforeEach, beforeAll } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DiscoveryStartPage } from './DiscoveryStartPage';

// Polyfill pointer-capture and scrollIntoView for Radix UI in jsdom
beforeAll(() => {
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.hasPointerCapture = Element.prototype.hasPointerCapture || (() => false);
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.setPointerCapture = Element.prototype.setPointerCapture || vi.fn();
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.releasePointerCapture = Element.prototype.releasePointerCapture || vi.fn();
  // eslint-disable-next-line @typescript-eslint/unbound-method
  Element.prototype.scrollIntoView = Element.prototype.scrollIntoView || vi.fn();
});

// --- mock return values ---------------------------------------------------

const mockWorkshop = { data: { discovery_questions_model_name: null } as Record<string, unknown> | undefined };
const mockAvailableModels = { data: [
  { name: 'databricks-claude-opus-4-5', state: 'READY', task: 'llm/v1/chat' },
] as Array<{ name: string; state: string; task: string }> | undefined };
const mockMlflowConfig = { data: null as Record<string, unknown> | null | undefined };
const mockUpdateModel = { mutate: vi.fn() };
const mockAllTraces = { data: [] as unknown[] };

vi.mock('@/hooks/useWorkshopApi', () => ({
  useWorkshop: () => mockWorkshop,
  useWorkshopDiscoveryConfig: () => mockWorkshop,
  useMLflowConfig: () => mockMlflowConfig,
  useAvailableModels: () => mockAvailableModels,
  useUpdateDiscoveryModel: () => mockUpdateModel,
  useAllTraces: () => mockAllTraces,
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'test-ws' }),
}));

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn() },
}));

describe('@spec:CUSTOM_LLM_PROVIDER_SPEC Custom provider in Discovery model selector', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWorkshop.data = { discovery_questions_model_name: null };
    mockAllTraces.data = [];
  });

  it('offers the custom provider option when a provider is configured and enabled', async () => {
    mockWorkshop.data = { discovery_questions_model_name: 'custom' };
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({ is_configured: true, is_enabled: true, provider_name: 'Acme LLM' }),
        { status: 200 },
      ),
    );

    render(<DiscoveryStartPage />);

    // Once the provider status fetch resolves, the conditional
    // SelectItem(value="custom") exists, so the selected value renders its label
    const trigger = screen.getByTestId('model-selector');
    await waitFor(() => expect(trigger).toHaveTextContent('Custom: Acme LLM'));

    // ...and the configuration summary indicates the custom provider is in use
    expect(screen.getByText(/custom: Acme LLM/)).toBeInTheDocument();
  });

  it('does not offer a custom option when no provider is configured', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ is_configured: false, is_enabled: false }), { status: 200 }),
    );

    render(<DiscoveryStartPage />);

    const trigger = screen.getByTestId('model-selector');
    await waitFor(() => expect(trigger).toHaveTextContent('Demo (static questions)'));

    expect(screen.queryByText(/Custom:/)).toBeNull();
  });
});
