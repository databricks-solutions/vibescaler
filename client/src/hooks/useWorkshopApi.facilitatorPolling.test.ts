// @spec ANNOTATION_SPEC
// @req Facilitator annotation stats poll every 15 seconds while the tab is in the foreground
import { describe, expect, it, vi, beforeEach } from 'vitest';
import type { UseQueryOptions } from '@tanstack/react-query';
import { useFacilitatorAnnotations, useFacilitatorAnnotationsWithUserDetails } from './useWorkshopApi';

const { useQueryMock } = vi.hoisted(() => ({
  useQueryMock: vi.fn(() => ({ data: undefined })),
}));

vi.mock('@tanstack/react-query', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@tanstack/react-query')>();
  return {
    ...actual,
    useQuery: useQueryMock,
  };
});

vi.mock('@/context/UserContext', () => ({
  useRoleCheck: () => ({ isFacilitator: true }),
}));

describe('facilitator annotation hooks polling', () => {
  beforeEach(() => {
    useQueryMock.mockClear();
  });

  it('useFacilitatorAnnotations polls every 15s in the foreground only', () => {
    useFacilitatorAnnotations('w1');

    expect(useQueryMock).toHaveBeenCalledTimes(1);
    const options = useQueryMock.mock.calls[0][0] as unknown as UseQueryOptions;
    expect(options.refetchInterval).toBe(15000);
    expect(options.refetchIntervalInBackground).toBe(false);
  });

  it('useFacilitatorAnnotationsWithUserDetails polls every 15s in the foreground only', () => {
    useFacilitatorAnnotationsWithUserDetails('w1');

    expect(useQueryMock).toHaveBeenCalledTimes(1);
    const options = useQueryMock.mock.calls[0][0] as unknown as UseQueryOptions;
    expect(options.refetchInterval).toBe(15000);
    expect(options.refetchIntervalInBackground).toBe(false);
  });
});
