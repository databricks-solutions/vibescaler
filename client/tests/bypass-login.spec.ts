import { test, chromium } from '@playwright/test';

test('bypass login and test new layout', async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--window-size=1920,1080']
  });
  
  const page = await browser.newPage();
  
  const mockUser = {
    id: 'test-facilitator-123',
    email: 'facilitator@test.com',
    name: 'Test Facilitator',
    role: 'facilitator',
    workshop_id: 'workshop1',
    status: 'active',
    created_at: new Date().toISOString()
  };

  await page.route('**/api/auth/session', async route => {
    await route.fulfill({
      json: {
        user: mockUser,
        permissions: {
          can_view_discovery: true,
          can_create_rubric: true,
          can_manage_workshop: true,
          can_manage_project: true,
        },
        provider: 'e2e_mock',
        provider_role: 'CAN_MANAGE',
      },
    });
  });
  
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  // Take screenshot of the new layout
  await page.screenshot({ path: 'bypassed-login-layout.png', fullPage: true });
  console.log('Screenshot saved as bypassed-login-layout.png');
  
  // Measure the new flush layout
  const measurements = await page.evaluate(() => {
    const sidebar = document.querySelector('.w-64');
    const mainArea = document.querySelector('.flex-1.flex.flex-col');
    const body = document.body;
    
    if (sidebar && mainArea) {
      const sidebarRect = sidebar.getBoundingClientRect();
      const mainRect = mainArea.getBoundingClientRect();
      
      return {
        sidebarWidth: sidebarRect.width,
        sidebarLeft: sidebarRect.left,
        mainContentWidth: mainRect.width,
        mainContentLeft: mainRect.left,
        viewportWidth: window.innerWidth,
        totalContentWidth: sidebarRect.width + mainRect.width,
        isFlushLeft: sidebarRect.left === 0
      };
    }
    return { error: 'Layout elements not found' };
  });
  
  console.log('Layout measurements:', measurements);
  
  // Try to navigate to rubric creation
  try {
    const rubricLink = page.locator('text=Rubric Creation').first();
    if (await rubricLink.isVisible()) {
      await rubricLink.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'rubric-bypassed-layout.png', fullPage: true });
      
      // Switch to focused view
      const focusedBtn = page.locator('button:has-text("Focused View")').first();
      if (await focusedBtn.isVisible()) {
        await focusedBtn.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: 'rubric-focused-bypassed-layout.png', fullPage: true });
        
        // Measure focused view
        const focusedMeasurements = await page.evaluate(() => {
          const content = document.querySelector('.w-full');
          return {
            contentWidth: content?.getBoundingClientRect().width,
            viewportWidth: window.innerWidth
          };
        });
        console.log('Focused view measurements:', focusedMeasurements);
      }
    }
  } catch (e) {
    console.log('Navigation error:', e);
  }
  
  await page.waitForTimeout(10000);
  await browser.close();
});