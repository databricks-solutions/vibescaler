/**
 * E2E coverage for annotation feedback propagation into the MLflow feedback
 * API boundary used by MemAlign.
 *
 * @spec ANNOTATION_SPEC
 */

import { test, expect } from '@playwright/test';
import { readFile, rm } from 'node:fs/promises';
import { TestScenario } from '../lib';
import { DEFAULT_API_URL } from '../lib/data';
import { submitAnnotation, waitForAnnotationInterface } from '../lib/actions/annotation';
import { beginAnnotation } from '../lib/actions/workshop';
import { WorkshopPhase } from '../lib/types';

const API_URL = process.env.E2E_API_URL ?? DEFAULT_API_URL;
const RECORDER_PATH = '../.test-results/mlflow-feedback.jsonl';

type MlflowFeedbackRecord = {
  event: string;
  trace_id: string;
  name?: string;
  value?: number;
  source_id?: string;
  rationale?: string | null;
  key?: string;
};

async function readMlflowFeedbackRecords(): Promise<MlflowFeedbackRecord[]> {
  const content = await readFile(RECORDER_PATH, 'utf-8');
  return content
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line) as MlflowFeedbackRecord);
}

test.describe('Annotation MLflow feedback sync', {
  tag: ['@spec:ANNOTATION_SPEC'],
}, () => {
  test('UI annotations from multiple SMEs reach MLflow feedback calls for MemAlign', {
    tag: [
      '@req:Annotations sync to MLflow as feedback on save (one entry per rubric question)',
      '@req:Feedback source is HUMAN with annotator\'s user_id',
    ],
  }, async ({ page }) => {
    await rm(RECORDER_PATH, { force: true });

    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'MLflow Feedback E2E' })
      .withFacilitator()
      .withSMEs(2)
      .withRubric({ question: 'Helpfulness: Rate helpfulness' })
      // Stay in intake during scenario setup. The test uploads an MLflow-backed
      // trace below, then explicitly starts annotation. Using RUBRIC/ANNOTATION
      // here would make TestScenario auto-start discovery before traces exist.
      .inPhase(WorkshopPhase.INTAKE)
      .withRealApi()
      .build();

    const workshopId = scenario.workshop.id;
    const mlflowTraceId = 'mlflow-feedback-e2e-trace-1';

    await page.request.post(`${API_URL}/workshops/${workshopId}/mlflow-config`, {
      data: {
        experiment_id: '12345',
        max_traces: 1,
        filter_string: '',
      },
    });

    const uploadResponse = await page.request.post(`${API_URL}/workshops/${workshopId}/traces`, {
      data: [
        {
          input: 'Customer asks whether the answer was helpful',
          output: 'The assistant gives a concise helpful answer',
          context: { spans: [] },
          mlflow_trace_id: mlflowTraceId,
          mlflow_experiment_id: '12345',
        },
      ],
    });
    expect(uploadResponse.ok()).toBe(true);

    await beginAnnotation(page, workshopId, API_URL);

    await page.goto(`/?workshop=${workshopId}`);
    await scenario.loginAs(scenario.users.sme[0]);
    await waitForAnnotationInterface(page);
    await submitAnnotation(page, {
      rating: 4,
      comment: 'SME one says the answer is helpful.',
    });

    await scenario.logout();
    await scenario.loginAs(scenario.users.sme[1]);
    await waitForAnnotationInterface(page);
    await submitAnnotation(page, {
      rating: 2,
      comment: 'SME two says the answer misses key context.',
    });

    await expect.poll(async () => {
      const records = await readMlflowFeedbackRecords().catch(() => []);
      return records.filter((r) => r.event === 'log_feedback').length;
    }, { timeout: 10_000 }).toBe(2);

    const records = await readMlflowFeedbackRecords();
    const feedback = records.filter((r) => r.event === 'log_feedback');
    expect(feedback).toHaveLength(2);

    expect(feedback.map((r) => r.trace_id)).toEqual([mlflowTraceId, mlflowTraceId]);
    expect(feedback.map((r) => r.name)).toEqual(['helpfulness_judge', 'helpfulness_judge']);
    expect(feedback.map((r) => r.value).sort()).toEqual([2, 4]);
    expect(new Set(feedback.map((r) => r.source_id))).toEqual(
      new Set([scenario.users.sme[0].id, scenario.users.sme[1].id])
    );
    expect(feedback.map((r) => r.rationale).filter(Boolean)).toEqual(
      expect.arrayContaining([
        'SME one says the answer is helpful.',
        'SME two says the answer misses key context.',
      ])
    );

    const alignTags = records.filter((r) => r.event === 'set_trace_tag' && r.key === 'align');
    expect(alignTags).toHaveLength(2);
    expect(alignTags.every((r) => r.value === 'true')).toBe(true);

    await scenario.cleanup();
  });
});
