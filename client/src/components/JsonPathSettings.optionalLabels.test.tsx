// @spec TRACE_DISPLAY_SPEC
// @req JSONPath fields are optional and clearly labeled as such
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { JsonPathSettings } from './JsonPathSettings';

const mockWorkshop = {
  id: 'ws-1',
  name: 'Test Workshop',
  input_jsonpath: null,
  output_jsonpath: null,
  span_attribute_filter: null,
};

const mockUseWorkshop = { data: mockWorkshop, isLoading: false };
const mockUpdateJsonPath = { mutateAsync: vi.fn(), isPending: false };
const mockPreviewJsonPath = { mutateAsync: vi.fn(), isPending: false };
const mockUpdateSpanFilter = { mutateAsync: vi.fn(), isPending: false };
const mockPreviewSpanFilter = { mutateAsync: vi.fn(), isPending: false };

vi.mock('@/context/WorkshopContext', () => ({
  useWorkshopContext: () => ({ workshopId: 'ws-1' }),
}));

vi.mock('@/hooks/useWorkshopApi', () => ({
  useWorkshop: () => mockUseWorkshop,
  useWorkshopDisplayConfig: () => ({
    data: mockUseWorkshop.data
      ? {
          input_jsonpath: mockUseWorkshop.data.input_jsonpath,
          output_jsonpath: mockUseWorkshop.data.output_jsonpath,
          span_attribute_filter: mockUseWorkshop.data.span_attribute_filter,
        }
      : undefined,
    isLoading: mockUseWorkshop.isLoading,
  }),
  useUpdateJsonPathSettings: () => mockUpdateJsonPath,
  usePreviewJsonPath: () => mockPreviewJsonPath,
  useUpdateSpanAttributeFilter: () => mockUpdateSpanFilter,
  usePreviewSpanFilter: () => mockPreviewSpanFilter,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe('@spec:TRACE_DISPLAY_SPEC JSONPath fields labeled optional', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseWorkshop.data = { ...mockWorkshop };
  });

  it('input and output JSONPath field labels are clearly marked optional', () => {
    render(<JsonPathSettings />);

    const inputLabel = document.querySelector('label[for="input-jsonpath"]');
    const outputLabel = document.querySelector('label[for="output-jsonpath"]');

    expect(inputLabel).not.toBeNull();
    expect(outputLabel).not.toBeNull();
    expect(inputLabel!.textContent).toContain('Input JSONPath');
    expect(inputLabel!.textContent!.toLowerCase()).toContain('optional');
    expect(outputLabel!.textContent).toContain('Output JSONPath');
    expect(outputLabel!.textContent!.toLowerCase()).toContain('optional');
  });

  it('input and output JSONPath fields are not required and render empty by default', () => {
    render(<JsonPathSettings />);

    const inputField = screen.getByLabelText(/Input JSONPath/i);
    const outputField = screen.getByLabelText(/Output JSONPath/i);

    expect(inputField).not.toBeRequired();
    expect(outputField).not.toBeRequired();
    expect(inputField).toHaveValue('');
    expect(outputField).toHaveValue('');
  });
});
