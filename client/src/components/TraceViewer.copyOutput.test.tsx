// @spec TRACE_DISPLAY_SPEC
// @req Copy Output copies the representation currently displayed (formatted vs raw)
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TraceViewer } from './TraceViewer';

// Mock clipboard API
const mockClipboardWrite = vi.fn().mockResolvedValue(undefined);
Object.assign(navigator, {
  clipboard: {
    writeText: mockClipboardWrite,
  },
});

vi.mock('@/hooks/useWorkshopApi', () => ({
  useInvalidateTraces: () => vi.fn(),
  useWorkshopDisplayConfig: () => ({ data: undefined }),
  useMLflowConfig: () => ({ data: undefined }),
}));

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'test-ws' }),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
}));

const FORMATTED_CONTENT = 'Hello, I am the formatted answer.';

const rawOutput = JSON.stringify({
  id: 'chatcmpl-123',
  object: 'chat.completion',
  model: 'gpt-4',
  choices: [
    {
      message: { role: 'assistant', content: FORMATTED_CONTENT },
      finish_reason: 'stop',
    },
  ],
});

const trace = {
  id: 'trace-1',
  input: '{"question": "Hi?"}',
  output: rawOutput,
};

describe('@spec:TRACE_DISPLAY_SPEC TraceViewer Copy Output', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('copies the formatted text when the formatted view is active', async () => {
    render(<TraceViewer trace={trace} />);

    // Formatted view is the default and shows the extracted LLM content
    expect(screen.getByText(FORMATTED_CONTENT)).toBeInTheDocument();

    fireEvent.click(screen.getByTitle('Copy Output'));

    await waitFor(() => {
      expect(mockClipboardWrite).toHaveBeenCalledWith(FORMATTED_CONTENT);
    });
  });

  it('copies pretty-printed raw JSON when the raw view is active', async () => {
    render(<TraceViewer trace={trace} />);

    fireEvent.click(screen.getByText('Show Raw JSON'));
    fireEvent.click(screen.getByTitle('Copy Output'));

    await waitFor(() => {
      expect(mockClipboardWrite).toHaveBeenCalledWith(
        JSON.stringify(JSON.parse(rawOutput), null, 2)
      );
    });
  });

  it('falls back to copying the display output when no LLM content is extracted', async () => {
    const plainTrace = {
      id: 'trace-2',
      input: '{}',
      output: '{"custom": "data"}',
    };
    render(<TraceViewer trace={plainTrace} />);

    fireEvent.click(screen.getByTitle('Copy Output'));

    await waitFor(() => {
      expect(mockClipboardWrite).toHaveBeenCalledWith('{"custom": "data"}');
    });
  });
});
