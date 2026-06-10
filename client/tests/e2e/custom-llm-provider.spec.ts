/**
 * E2E tests for Custom LLM Provider feature
 *
 * These tests verify the Configuration and Connection Testing success criteria
 * from CUSTOM_LLM_PROVIDER_SPEC.md:
 * - Configuration UI is accessible in Judge Tuning phase
 * - Users can configure custom LLM provider (provider name, URL, API key, model)
 * - Test connection validates configuration
 * - Configuration can be updated and deleted
 *
 * NOTE: judge evaluation does not consume custom providers (roadmap in the
 * spec), so nothing here asserts judge model selection or provider switching
 * for evaluation.
 */

import { test, expect } from '@playwright/test';
import { TestScenario } from '../lib';
import {
  navigateToCustomLlmProvider,
  expandProviderConfig,
  configureProvider,
  deleteProviderConfig,
  updateProviderConfig,
} from '../lib/actions/custom-llm-provider';

test.describe('Custom LLM Provider Configuration', { tag: ['@spec:CUSTOM_LLM_PROVIDER_SPEC']}, () => {
  test('facilitator can access custom LLM provider config in judge tuning', { tag: ['@req:Users can configure custom LLM provider via UI'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'LLM Provider Test Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(3)
      .withRubric({ question: 'How helpful is this response?' })
      .withAnnotation({ rating: 4, comment: 'Good response' })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'LLM Provider Test Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);

    await scenario.cleanup();
  });

  test('facilitator can configure and test custom LLM provider', { tag: ['@req:Test Connection button verifies endpoint is reachable', '@req:Response time is displayed on success'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Config Test Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withRubric({ question: 'Quality assessment' })
      .withAnnotation({ rating: 3 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'Config Test Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await configureProvider(page, {
      providerName: 'Azure OpenAI',
      baseUrl: 'https://my-resource.openai.azure.com/openai/deployments/gpt-4',
      modelName: 'gpt-4',
      apiKey: 'test-api-key-12345',
    });

    // Test Connection button should be available after saving
    await expect(page.getByRole('button', { name: /Test Connection/i })).toBeVisible({ timeout: 5000 });
    await page.getByRole('button', { name: /Test Connection/i }).click();

    await expect(page.getByText(/Successfully connected/i)).toBeVisible({ timeout: 10000 });
    // Response time is displayed alongside the success message
    await expect(page.getByText(/\(\d+ms\)/)).toBeVisible({ timeout: 5000 });

    await scenario.cleanup();
  });

  test('facilitator can delete custom LLM provider configuration', { tag: ['@req:Configuration can be deleted, removing both the stored config and the in-memory API key'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Delete Test Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withRubric()
      .withAnnotation({ rating: 4 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'Delete Test Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await configureProvider(page, {
      providerName: 'Test Provider',
      baseUrl: 'https://example.com',
      modelName: 'test-model',
      apiKey: 'test-key',
    });

    await deleteProviderConfig(page);

    await scenario.cleanup();
  });

  test('shows stored badge after saving API key', { tag: ['@req:API key is stored securely in memory (not database)'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'API Key Badge Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withRubric()
      .withAnnotation({ rating: 5 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'API Key Badge Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await configureProvider(page, {
      providerName: 'Provider With Key',
      baseUrl: 'https://example.com',
      modelName: 'model',
      apiKey: 'secret-key-123',
    });

    // Verify stored badge is shown (may be "Stored" or "API Key Stored")
    await expect(page.getByText(/Stored/)).toBeVisible({ timeout: 5000 });

    await scenario.cleanup();
  });

  test('validation requires all fields', { tag: ['@req:Users can configure custom LLM provider via UI'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Validation Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withRubric()
      .withAnnotation({ rating: 3 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'Validation Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await expandProviderConfig(page);

    // Try to save without filling fields
    await page.getByRole('button', { name: /Save Configuration/i }).click();

    await expect(page.getByText('Please fill in all required fields')).toBeVisible({ timeout: 5000 });

    await scenario.cleanup();
  });

  // NOTE: the judge model selector does NOT offer a custom provider option
  // (roadmap in CUSTOM_LLM_PROVIDER_SPEC); this test only verifies the saved
  // configuration is reflected back in the configuration form.
  test('saved provider configuration is reflected in the configuration form', { tag: ['@req:Base URL, API key, and model name are captured'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Model Selector Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(3)
      .withRubric({ question: 'Rate the response quality' })
      .withAnnotation({ rating: 4 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'Model Selector Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await configureProvider(page, {
      providerName: 'My Custom Provider',
      baseUrl: 'https://custom-api.example.com/v1',
      modelName: 'custom-model-1',
      apiKey: 'custom-key-123',
    });

    // Verify the custom provider config is saved
    await expect(page.getByLabel('Provider Name')).toHaveValue('My Custom Provider', { timeout: 5000 });
    await expect(page.getByLabel('Base URL')).toHaveValue('https://custom-api.example.com/v1', { timeout: 5000 });
    await expect(page.getByLabel('Model Name')).toHaveValue('custom-model-1', { timeout: 5000 });

    await scenario.cleanup();
  });

  // NOTE: this updates the stored provider configuration in place; it does not
  // (and cannot, yet) switch which provider judge evaluation uses — that
  // integration is roadmap in CUSTOM_LLM_PROVIDER_SPEC.
  test('provider configuration can be updated in place', { tag: ['@req:Configuration can be updated without losing other workshop data'] }, async ({ page }) => {
    const scenario = await TestScenario.create(page)
      .withWorkshop({ name: 'Switch Provider Workshop' })
      .withFacilitator()
      .withParticipants(1)
      .withTraces(2)
      .withRubric({ question: 'Assess response' })
      .withAnnotation({ rating: 3 })
      .inPhase('tuning')
      .build();

    await page.goto('/');
    await scenario.loginAs(scenario.facilitator);

    await expect(page.getByRole('heading', { name: 'Switch Provider Workshop' })).toBeVisible({ timeout: 15000 });

    await navigateToCustomLlmProvider(page);
    await configureProvider(page, {
      providerName: 'Provider A',
      baseUrl: 'https://provider-a.example.com',
      modelName: 'model-a',
      apiKey: 'key-a',
    });

    await expect(page.getByLabel('Provider Name')).toHaveValue('Provider A', { timeout: 5000 });

    // Update to Provider B
    await updateProviderConfig(page, {
      providerName: 'Provider B',
      baseUrl: 'https://provider-b.example.com',
      modelName: 'model-b',
      apiKey: 'key-b',
    });

    await expect(page.getByLabel('Provider Name')).toHaveValue('Provider B', { timeout: 5000 });

    await scenario.cleanup();
  });
});
