import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

// Log ALL network requests
page.on('request', req => {
  if (req.url().includes('api.minimax') || req.url().includes('cognito')) {
    console.log(`>> ${req.method()} ${req.url().substring(0, 120)}`);
  }
});
page.on('response', resp => {
  if (resp.url().includes('api.minimax') || resp.url().includes('cognito')) {
    console.log(`<< ${resp.status()} ${resp.url().substring(0, 120)}`);
  }
});
page.on('console', msg => console.log(`[console.${msg.type()}] ${msg.text().substring(0, 200)}`));

// Login
console.log('--- LOGIN ---');
await page.goto('https://minimax.villamarket.ai/login', { waitUntil: 'networkidle' });
await page.fill('input[type="email"]', 'test@minimax.villamarket.ai');
await page.fill('input[type="password"]', 'TestPass99');
await page.click('button:has-text("Sign In")');

// Wait for redirect
await page.waitForURL('**/dashboard', { timeout: 15000 }).catch(() => {});
console.log('URL:', page.url());
console.log('--- WAITING FOR DASHBOARD TO LOAD ---');
await page.waitForTimeout(10000);

// Check state
const body = await page.textContent('body');
console.log('Has Create Key:', body.includes('Create API Key'));
console.log('Has loading spinner:', body.includes('loading') || !body.includes('Create API Key'));
console.log('Has error:', body.includes('Failed'));

await page.screenshot({ path: '/tmp/dashboard-debug2.png' });
await browser.close();
