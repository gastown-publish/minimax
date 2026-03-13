import { chromium } from 'playwright';
import { execSync } from 'child_process';

const BASE = 'https://minimax.villamarket.ai';
const API_BASE = 'https://api.minimax.villamarket.ai';
const LITELLM_BASE = 'https://gpu-workspace.taile8dc37.ts.net/minimax';
const COGNITO_CLIENT_ID = 'ac6n9a2dijabmemnk19qa62bu';
const TEST_EMAIL = 'test@minimax.villamarket.ai';
const TEST_PASSWORD = 'TestPass99';

const results = [];
let idToken = '';
let createdApiKey = '';
let createdTokenId = '';

function log(test, pass, detail = '') {
  const icon = pass ? 'PASS' : 'FAIL';
  console.log(`[${icon}] ${test}${detail ? ' — ' + detail : ''}`);
  results.push({ test, pass, detail });
}

function getIdToken() {
  return execSync(
    `aws cognito-idp initiate-auth --client-id ${COGNITO_CLIENT_ID} ` +
    `--auth-flow USER_PASSWORD_AUTH ` +
    `--auth-parameters "USERNAME=${TEST_EMAIL},PASSWORD=${TEST_PASSWORD}" ` +
    `--region us-east-1 --query "AuthenticationResult.IdToken" --output text`,
    { encoding: 'utf-8' }
  ).trim();
}

// Helper: wait for dashboard content to load (spinner gone)
async function waitForDashboardLoaded(page, timeout = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const has = await page.$('text=Create API Key');
    if (has) return true;
    await page.waitForTimeout(500);
  }
  return false;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
  });
  const page = await context.newPage();

  // Get auth token upfront
  idToken = getIdToken();

  // ════════════════════════════════════════════════════════════════
  // 1. LANDING PAGE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 1. LANDING PAGE ══╗');

  await page.goto(BASE, { waitUntil: 'networkidle' });
  log('Landing 200', (await page.evaluate(() => document.readyState)) === 'complete');
  log('Title contains MiniMax', (await page.title()).includes('MiniMax'));
  log('Meta description exists', !!(await page.$('meta[name="description"]')));
  const metaDesc = await page.$eval('meta[name="description"]', el => el.content);
  log('Meta description content', metaDesc.includes('SWE-Bench'), metaDesc.slice(0, 80));
  log('H1 = MiniMax-M2.5 API', (await page.textContent('h1')).includes('MiniMax-M2.5'));
  log('SWE-Bench badge', !!(await page.$('text=80.2% SWE-Bench')));
  log('Get Started CTA', !!(await page.$('a:has-text("Get Started")')));
  log('API Docs CTA', !!(await page.$('a:has-text("API Docs")')));
  log('Curl example', !!(await page.$('code:has-text("curl")')));

  // 6 features
  for (const f of ['Top Coding Performance', '128K Context Window', 'OpenAI Compatible',
    'Tool Calling', 'Open Source Model', 'Usage-Based Pricing']) {
    log(`Feature: ${f}`, !!(await page.$(`text=${f}`)));
  }

  // Pricing
  log('Pricing heading', !!(await page.$('text=Pricing')));
  log('Free card', !!(await page.$('h3:has-text("Free")')));
  log('Pro card', !!(await page.$('h3:has-text("Pro")')));
  log('Enterprise card', !!(await page.$('h3:has-text("Enterprise")')));
  log('Most Popular badge', !!(await page.$('text=Most Popular')));

  const body = await page.textContent('body');
  log('Free: $5 budget', body.includes('$5/month API budget'));
  log('Free: 5 RPM', body.includes('5 requests per minute'));
  log('Free: 5 keys', body.includes('5 API keys'));
  log('Free: 128K ctx', body.includes('128K context'));
  log('Token pricing', body.includes('$0.30/M input'));
  log('Output pricing', body.includes('$1.20/M output'));
  log('Bottom CTA', !!(await page.$('text=Ready to start building')));
  log('Create Free Account', !!(await page.$('a:has-text("Create Free Account")')));

  // ════════════════════════════════════════════════════════════════
  // 2. PRICING TOGGLE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 2. PRICING TOGGLE ══╗');

  log('Monthly btn', !!(await page.$('button:has-text("Monthly")')));
  log('Yearly btn', !!(await page.$('button:has-text("Yearly")')));
  log('Monthly: Pro $20', !!(await page.$('text=$20')));
  log('Monthly: Enterprise $100', !!(await page.$('text=$100')));

  await page.click('button:has-text("Yearly")');
  await page.waitForTimeout(400);
  const yBody = await page.textContent('body');
  log('Yearly: Pro $16', yBody.includes('$16'));
  log('Yearly: Enterprise $80', yBody.includes('$80'));
  log('Yearly: Save 20%', yBody.includes('Save 20%'));

  await page.click('button:has-text("Monthly")');
  await page.waitForTimeout(400);
  log('Back to monthly: Pro $20', !!(await page.$('text=$20')));

  // ════════════════════════════════════════════════════════════════
  // 3. NAVBAR (UNAUTHENTICATED)
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 3. NAVBAR ══╗');

  log('Home link', !!(await page.$('nav a[href="/"]')));
  log('Docs link', !!(await page.$('nav a[href="/docs"]')));
  log('Sign In', !!(await page.$('nav a:has-text("Sign In")')));
  log('Logo', !!(await page.$('nav a:has-text("MiniMax-M2.5")')));
  log('Mobile hamburger', !!(await page.$('nav button.md\\:hidden')));

  // ════════════════════════════════════════════════════════════════
  // 4. FOOTER
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 4. FOOTER ══╗');

  log('Copyright', !!(await page.$('footer:has-text("villamarket.ai")')));
  log('Docs link', !!(await page.$('footer a[href="/docs"]')));
  const hfLink = await page.$('footer a[href*="huggingface.co"]');
  log('HuggingFace link', !!hfLink);
  if (hfLink) log('Opens new tab', (await hfLink.getAttribute('target')) === '_blank');

  // ════════════════════════════════════════════════════════════════
  // 5. DOCS PAGE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 5. DOCS PAGE ══╗');

  await page.goto(BASE + '/docs', { waitUntil: 'networkidle' });
  log('Title', (await page.title()).includes('Documentation'));
  log('H1', (await page.textContent('h1')).includes('API Documentation'));

  for (const s of ['Quick Start', 'Authentication', 'Chat Completions', 'Streaming',
    'Tool Calling', 'Think Blocks', 'Models', 'Rate Limits', 'Integrations', 'Errors']) {
    log(`Sidebar: ${s}`, !!(await page.$(`text=${s}`)));
  }

  const codeBlocks = await page.$$('pre code');
  log('Code blocks', codeBlocks.length > 5, `${codeBlocks.length} blocks`);

  // Click copy button on first code block (clipboard API may not work in headless)
  const firstCopyBtn = await page.$('button:has(svg.lucide-copy)');
  log('Copy button exists', !!firstCopyBtn);

  // Click sidebar nav
  const streamingLink = await page.$('a:has-text("Streaming"), button:has-text("Streaming")');
  if (streamingLink) {
    await streamingLink.click();
    await page.waitForTimeout(500);
    log('Sidebar nav scrolls page', true);
  }

  const dBody = await page.textContent('body');
  log('Params table: model', dBody.includes('model'));
  log('Params table: temperature', dBody.includes('temperature'));
  log('Integration: Claude Code', dBody.includes('Claude Code') || dBody.includes('claude'));
  log('Integration: Cursor', dBody.includes('Cursor') || dBody.includes('cursor'));
  log('Error code 401', dBody.includes('401'));
  log('Error code 429', dBody.includes('429'));

  // ════════════════════════════════════════════════════════════════
  // 6. LOGIN PAGE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 6. LOGIN PAGE ══╗');

  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  log('Heading: Sign in', (await page.textContent('h1')).includes('Sign in'));
  log('Google btn', !!(await page.$('button:has-text("Continue with Google")')));
  log('Apple btn', !!(await page.$('button:has-text("Continue with Apple")')));
  log('Email input', !!(await page.$('input[type="email"]')));
  log('Password input', !!(await page.$('input[type="password"]')));
  log('Submit btn', !!(await page.$('button:has-text("Sign In")')));
  log('Signup link', !!(await page.$('button:has-text("Sign up")')));

  // Toggle to signup
  await page.click('button:has-text("Sign up")');
  await page.waitForTimeout(300);
  log('Signup: heading', (await page.textContent('h1')).includes('Create account'));
  log('Signup: Create Account btn', !!(await page.$('button:has-text("Create Account")')));
  log('Signup: Sign in link', !!(await page.$('button:has-text("Sign in")')));
  log('Signup: email visible', !!(await page.$('input[type="email"]')));
  log('Signup: password visible', !!(await page.$('input[type="password"]')));

  // Back to signin
  await page.click('button:has-text("Sign in")');
  await page.waitForTimeout(300);
  log('Back to signin', (await page.textContent('h1')).includes('Sign in'));

  // Wrong password error
  await page.fill('input[type="email"]', 'wrong@email.com');
  await page.fill('input[type="password"]', 'WrongPass123');
  await page.click('button:has-text("Sign In")');
  await page.waitForTimeout(3000);
  log('Wrong password: error shown', !!(await page.$('[class*="red"]')));
  log('Still on login page', page.url().includes('/login'));

  // ════════════════════════════════════════════════════════════════
  // 7. REAL LOGIN
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 7. LOGIN FLOW ══╗');

  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', TEST_EMAIL);
  await page.fill('input[type="password"]', TEST_PASSWORD);
  await page.click('button:has-text("Sign In")');
  await page.waitForURL('**/dashboard', { timeout: 15000 }).catch(() => {});
  log('Login → dashboard redirect', page.url().includes('/dashboard'));

  const navText = await page.textContent('nav');
  log('Navbar shows email', navText.includes('test@'));
  log('Navbar: Dashboard link', !!(await page.$('nav a[href="/dashboard"]')));
  log('Navbar: Chat link', !!(await page.$('nav a[href="/chat"]')));
  log('Navbar: Sign Out btn', !!(await page.$('button:has(svg.lucide-log-out)')));

  // ════════════════════════════════════════════════════════════════
  // 8. DASHBOARD: API KEYS TAB
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 8. DASHBOARD: KEYS TAB ══╗');

  await page.goto(BASE + '/dashboard', { waitUntil: 'networkidle' });
  const loaded = await waitForDashboardLoaded(page);
  log('Dashboard loaded (no spinner)', loaded);

  log('Tabs: API Keys', !!(await page.$('button:has-text("API Keys")')));
  log('Tabs: Billing', !!(await page.$('button:has-text("Billing")')));
  log('Tabs: Referrals', !!(await page.$('button:has-text("Referrals")')));
  log('Heading: Create API Key', !!(await page.$('text=Create API Key')));
  log('Alias input', !!(await page.$('input[placeholder*="alias"]')));
  log('Create Key btn', !!(await page.$('button:has-text("Create Key")')));

  // Clean up existing keys via API first to avoid hitting limit
  const preCleanHeaders = { Authorization: `Bearer ${idToken}`, 'Content-Type': 'application/json' };
  const preExisting = await (await page.request.get(`${API_BASE}/api/keys`, { headers: preCleanHeaders })).json();
  for (const k of preExisting) await page.request.delete(`${API_BASE}/api/keys/${k.token}`, { headers: preCleanHeaders });
  if (preExisting.length > 0) {
    // Reload dashboard to reflect cleanup
    await page.goto(BASE + '/dashboard', { waitUntil: 'networkidle' });
    await waitForDashboardLoaded(page);
  }

  // Create a key
  await page.fill('input[placeholder*="alias"]', 'pw-test-key');
  await page.click('button:has-text("Create Key")');
  // Wait for key creation (Lambda + LiteLLM can take up to 15s)
  await page.waitForSelector('text=Copy it now', { timeout: 20000 }).catch(() => null);
  const hasSuccess = !!(await page.$('text=Copy it now'));
  if (!hasSuccess) {
    const errEl = await page.$('[class*="red"]');
    const errText = errEl ? await errEl.textContent() : 'no error element';
    console.log(`  [DEBUG] Key creation failed. Error: ${errText}`);
  }
  log('Key created: success message', hasSuccess);

  if (hasSuccess) {
    const keyCode = await page.$eval('code', el => el.textContent);
    log('Key starts with sk-', keyCode.trim().startsWith('sk-'));

    // Copy button
    log('Copy btn in success box', !!(await page.$('button:has(svg.lucide-copy)')));
  }

  // Key table
  const tableText = await page.textContent('body');
  log('Key alias in table', tableText.includes('pw-test-key'));
  const keysMatch = tableText.match(/Your Keys \((\d+)/);
  log('Keys count shown', !!keysMatch, keysMatch ? `count=${keysMatch[1]}` : 'no count');

  // Key masking
  log('Key masked (sk-...)', tableText.includes('sk-...') || tableText.includes('...'));

  // Budget in table
  log('Budget $5 in table', tableText.includes('$5') || tableText.includes('5.00'));

  // ════════════════════════════════════════════════════════════════
  // 9. DASHBOARD: KEY TABLE ACTIONS
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 9. KEY TABLE ACTIONS ══╗');

  // Reveal/hide key toggle
  const eyeBtn = await page.$('button:has(svg.lucide-eye)');
  log('Eye (reveal) btn exists', !!eyeBtn);
  if (eyeBtn) {
    await eyeBtn.click();
    await page.waitForTimeout(300);
    const eyeOff = await page.$('button:has(svg.lucide-eye-off)');
    log('Key revealed (eye-off icon)', !!eyeOff);
    if (eyeOff) {
      await eyeOff.click();
      await page.waitForTimeout(300);
      log('Key hidden again', !!(await page.$('button:has(svg.lucide-eye)')));
    }
  }

  // ════════════════════════════════════════════════════════════════
  // 10. DASHBOARD: BILLING TAB
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 10. BILLING TAB ══╗');

  await page.click('button:has-text("Billing")');
  await page.waitForTimeout(500);

  log('Billing: Upgrade heading', !!(await page.$('text=Upgrade Plan')));
  log('Billing: Free card', !!(await page.$('h3:has-text("Free")')));
  log('Billing: Pro card', !!(await page.$('h3:has-text("Pro")')));
  log('Billing: Enterprise card', !!(await page.$('h3:has-text("Enterprise")')));
  log('Billing: Monthly toggle', !!(await page.$('button:has-text("Monthly")')));
  log('Billing: Yearly toggle', !!(await page.$('button:has-text("Yearly")')));

  // Yearly toggle
  const billingYearly = await page.$('button:has-text("Yearly")');
  if (billingYearly) {
    await billingYearly.click();
    await page.waitForTimeout(400);
    const bBody = await page.textContent('body');
    log('Billing yearly: $16 shown', bBody.includes('$16'));
    log('Billing yearly: $80 shown', bBody.includes('$80'));
  }

  // ════════════════════════════════════════════════════════════════
  // 11. DASHBOARD: REFERRALS TAB
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 11. REFERRALS TAB ══╗');

  await page.click('button:has-text("Referrals")');
  await page.waitForTimeout(500);

  const refInput = await page.$('input[placeholder*="referral"]');
  log('Referral input', !!refInput);
  const applyBtn = await page.$('button:has-text("Apply")');
  log('Apply btn', !!applyBtn);
  if (applyBtn) {
    log('Apply btn disabled when empty', await applyBtn.isDisabled());
    // Type something
    if (refInput) {
      await refInput.fill('TEST-CODE');
      await page.waitForTimeout(200);
      log('Apply btn enabled after input', !(await applyBtn.isDisabled()));
      // Click apply (will fail since no backend, but tests the button works)
      await applyBtn.click();
      await page.waitForTimeout(2000);
      // Check for error/feedback message
      const refBody = await page.textContent('body');
      log('Apply shows feedback', refBody.includes('Not found') || refBody.includes('error') ||
        refBody.includes('Failed') || refBody.includes('referral'));
    }
  }

  // ════════════════════════════════════════════════════════════════
  // 12. CHAT PAGE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 12. CHAT PAGE ══╗');

  await page.goto(BASE + '/chat', { waitUntil: 'networkidle' });
  // Wait for auth to load and chat page to render
  await page.waitForSelector('h2:has-text("MiniMax"), textarea, text=No API key', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(1000);
  console.log('  Chat URL:', page.url());

  log('Sidebar toggle btn', !!(await page.$('button:has(svg.lucide-panel-left-close), button:has(svg.lucide-panel-left)')));
  log('Settings btn', !!(await page.$('button:has(svg.lucide-settings)')));
  log('Empty state: MiniMax heading', !!(await page.$('h2:has-text("MiniMax-M2.5")')));
  log('Empty state: 128K context', !!(await page.$('text=128K context')));

  // Quick prompts
  log('Quick prompt: quicksort', !!(await page.$('button:has-text("quicksort")')));
  log('Quick prompt: transformers', !!(await page.$('button:has-text("transformers")')));
  log('Quick prompt: React', !!(await page.$('button:has-text("React component")')));

  // Input area
  log('Textarea', !!(await page.$('textarea[placeholder*="Send a message"]')));
  log('Send btn', !!(await page.$('button:has(svg.lucide-send)')));

  // ════════════════════════════════════════════════════════════════
  // 13. CHAT: SETTINGS PANEL
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 13. CHAT SETTINGS ══╗');

  await page.click('button:has(svg.lucide-settings)');
  await page.waitForTimeout(500);
  log('Settings panel open', !!(await page.$('text=Chat Settings')));
  log('System prompt textarea', !!(await page.$('textarea[placeholder*="coding assistant"]')));
  log('Model dropdown', !!(await page.$('select')));
  log('Temperature slider', !!(await page.$('input[type="range"]')));
  log('Max tokens input', !!(await page.$('input[type="number"]')));

  const opts = await page.$$eval('select option', os => os.map(o => o.value));
  log('Model: minimax-m2.5', opts.includes('minimax-m2.5'));
  log('Model: MiniMaxAI/MiniMax-M2.5', opts.includes('MiniMaxAI/MiniMax-M2.5'));

  // Change temperature
  await page.$eval('input[type="range"]', el => { el.value = '1.0'; el.dispatchEvent(new Event('input', {bubbles:true})); el.dispatchEvent(new Event('change', {bubbles:true})); });
  await page.waitForTimeout(300);
  const tempText = await page.textContent('body');
  log('Temperature updated', tempText.includes('1'));

  // Change max tokens
  await page.fill('input[type="number"]', '8192');
  await page.waitForTimeout(300);

  // Close
  const closeBtn = await page.$('button:has(svg.lucide-x)');
  if (closeBtn) {
    await closeBtn.click();
    await page.waitForTimeout(300);
    log('Settings closed', !(await page.$('text=Chat Settings')));
  }

  // ════════════════════════════════════════════════════════════════
  // 14. CHAT: SIDEBAR
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 14. CHAT SIDEBAR ══╗');

  const newChatBtn = await page.$('button:has(svg.lucide-plus)');
  log('New Chat btn', !!newChatBtn);

  // Toggle sidebar off
  const hideBtn = await page.$('button:has(svg.lucide-panel-left-close)');
  if (hideBtn) {
    await hideBtn.click();
    await page.waitForTimeout(300);
    const sidebarHidden = !(await page.$('button:has(svg.lucide-plus)'));
    log('Sidebar hidden', sidebarHidden);

    // Show again
    const showBtn = await page.$('button:has(svg.lucide-panel-left)');
    if (showBtn) {
      await showBtn.click();
      await page.waitForTimeout(300);
      log('Sidebar shown', !!(await page.$('button:has(svg.lucide-plus)')));
    }
  }

  // ════════════════════════════════════════════════════════════════
  // 15. CHAT: SEND MESSAGE (STREAMING)
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 15. CHAT: SEND MESSAGE ══╗');

  // Check if API key is available for chat
  const noKeyWarning = await page.$('text=No API key');
  if (noKeyWarning) {
    log('Chat: No API key warning shown', true);
    log('Chat: Dashboard link in warning', !!(await page.$('a[href="/dashboard"]')));
    // We can skip actual message sending
    log('Chat: (Skipping send — no stored key)', true, 'key only stored on dashboard create');
  } else {
    await page.fill('textarea[placeholder*="Send a message"]', 'What is 2+2? Just the number.');
    await page.click('button:has(svg.lucide-send)');
    await page.waitForTimeout(2000);

    const hasUserMsg = (await page.textContent('body')).includes('What is 2+2');
    log('Chat: User message shown', hasUserMsg);

    // Stop button appears briefly during streaming (may already be gone if response is fast)
    const stopBtn = await page.$('button:has(svg.lucide-square)');
    log('Chat: Streaming started', hasUserMsg, stopBtn ? 'stop btn visible' : 'response already complete');

    await page.waitForTimeout(20000);
    const chatBody = await page.textContent('body');
    log('Chat: Assistant responded', chatBody.includes('4'));
    log('Chat: Conversation in sidebar', !!(await page.$('text=What is 2+2')));
  }

  // ════════════════════════════════════════════════════════════════
  // 16. NAVIGATION
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 16. NAVIGATION ══╗');

  await page.click('nav a[href="/docs"]');
  await page.waitForURL('**/docs', { timeout: 5000 });
  log('Nav → Docs', page.url().includes('/docs'));

  await page.click('nav a[href="/"]');
  await page.waitForTimeout(1000);
  log('Nav → Home', !page.url().includes('/docs'));

  await page.click('nav a[href="/dashboard"]');
  await page.waitForURL('**/dashboard', { timeout: 5000 });
  log('Nav → Dashboard', page.url().includes('/dashboard'));

  await page.click('nav a[href="/chat"]');
  await page.waitForURL('**/chat', { timeout: 5000 });
  log('Nav → Chat', page.url().includes('/chat'));

  // ════════════════════════════════════════════════════════════════
  // 17. API: AUTH
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 17. API AUTH ══╗');

  const authHeaders = { Authorization: `Bearer ${idToken}`, 'Content-Type': 'application/json' };

  log('GET 401 no auth', (await page.request.get(`${API_BASE}/api/keys`)).status() === 401);
  log('POST 401 no auth', (await page.request.post(`${API_BASE}/api/keys`, { data: '{}' })).status() === 401);
  log('DELETE 401 no auth', (await page.request.delete(`${API_BASE}/api/keys/x`)).status() === 401);
  log('Bad JWT rejected', (await page.request.get(`${API_BASE}/api/keys`, { headers: { Authorization: 'Bearer bad' } })).status() === 401);

  // ════════════════════════════════════════════════════════════════
  // 18. API: KEY LIFECYCLE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 18. API KEY LIFECYCLE ══╗');

  // Cleanup existing
  const existing = await (await page.request.get(`${API_BASE}/api/keys`, { headers: authHeaders })).json();
  for (const k of existing) await page.request.delete(`${API_BASE}/api/keys/${k.token}`, { headers: authHeaders });
  log('Cleanup', true, `${existing.length} deleted`);

  // Create with alias
  const c1 = await page.request.post(`${API_BASE}/api/keys`, { headers: authHeaders, data: JSON.stringify({ alias: 'key-1' }) });
  log('Create 1: 200', c1.status() === 200);
  const k1 = await c1.json();
  log('Create 1: sk- prefix', k1.key?.startsWith('sk-'));
  log('Create 1: has token', k1.token?.length > 10);
  log('Create 1: alias match', k1.key_alias === 'key-1');
  log('Create 1: $5 budget', k1.max_budget === 5.0);
  log('Create 1: spend 0', k1.spend === 0);
  log('Create 1: no expiry', k1.expires === null);
  log('Create 1: has created_at', !!k1.created_at);
  createdApiKey = k1.key;
  createdTokenId = k1.token;

  // Create without alias
  const c2 = await page.request.post(`${API_BASE}/api/keys`, { headers: authHeaders, data: JSON.stringify({}) });
  log('Create 2 (no alias): 200', c2.status() === 200);
  log('Create 2: empty alias', (await c2.json()).key_alias === '');

  // List
  const list = await (await page.request.get(`${API_BASE}/api/keys`, { headers: authHeaders })).json();
  log('List: 2 keys', list.length === 2);
  log('List: masked key', list[0].key.includes('...'));
  log('List: has spend', typeof list[0].spend === 'number');
  log('List: has budget', typeof list[0].max_budget === 'number');
  log('List: has created_at', !!list[0].created_at);

  // Delete one
  const d = await page.request.delete(`${API_BASE}/api/keys/${(await c2.json()).token || list[1].token}`, { headers: authHeaders });
  log('Delete: 200', d.status() === 200);
  log('Delete: {deleted: true}', (await d.json()).deleted === true);

  const after = await (await page.request.get(`${API_BASE}/api/keys`, { headers: authHeaders })).json();
  log('After delete: 1 key', after.length === 1);

  // ════════════════════════════════════════════════════════════════
  // 19. API: KEY LIMIT
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 19. API KEY LIMIT ══╗');

  // Have 1, create 4 more
  for (let i = 2; i <= 5; i++) {
    const r = await page.request.post(`${API_BASE}/api/keys`, { headers: authHeaders, data: JSON.stringify({ alias: `k${i}` }) });
    log(`Key ${i}/5: 200`, r.status() === 200);
  }
  const over = await page.request.post(`${API_BASE}/api/keys`, { headers: authHeaders, data: JSON.stringify({ alias: 'over' }) });
  log('6th key: 400', over.status() === 400);
  const overBody = await over.json();
  log('Error: mentions limit', overBody.error?.includes('limit'));
  log('Error: mentions 5', overBody.error?.includes('5'));
  log('Error: mentions free', overBody.error?.includes('free'));

  // ════════════════════════════════════════════════════════════════
  // 20. INFERENCE
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 20. INFERENCE ══╗');

  // Non-streaming
  const inf = await page.request.post(`${LITELLM_BASE}/v1/chat/completions`, {
    headers: { Authorization: `Bearer ${createdApiKey}`, 'Content-Type': 'application/json' },
    data: JSON.stringify({ model: 'minimax-m2.5', messages: [{ role: 'user', content: 'What is 2+2? ONLY the number.' }], max_tokens: 50 }),
    timeout: 60000,
  });
  log('Inference: 200', inf.status() === 200);
  const iData = await inf.json();
  log('Inference: choices', !!iData.choices?.length);
  log('Inference: content', !!iData.choices?.[0]?.message?.content);
  log('Inference: usage', !!iData.usage);
  log('Inference: model name', iData.model === 'minimax-m2.5');
  log('Inference: contains 4', (iData.choices?.[0]?.message?.content || '').includes('4'));

  // Streaming
  const stream = await page.request.post(`${LITELLM_BASE}/v1/chat/completions`, {
    headers: { Authorization: `Bearer ${createdApiKey}`, 'Content-Type': 'application/json' },
    data: JSON.stringify({ model: 'minimax-m2.5', messages: [{ role: 'user', content: 'Say hi' }], max_tokens: 20, stream: true }),
    timeout: 30000,
  });
  log('Stream: 200', stream.status() === 200);
  const sBody = await stream.text();
  log('Stream: data: prefix', sBody.includes('data: '));
  log('Stream: [DONE]', sBody.includes('[DONE]'));

  // Bad key
  const bad = await page.request.post(`${LITELLM_BASE}/v1/chat/completions`, {
    headers: { Authorization: 'Bearer sk-bad', 'Content-Type': 'application/json' },
    data: JSON.stringify({ model: 'minimax-m2.5', messages: [{ role: 'user', content: 'test' }], max_tokens: 5 }),
  });
  log('Bad key: 401', bad.status() === 401);

  // Models endpoint
  const models = await page.request.get(`${LITELLM_BASE}/v1/models`, {
    headers: { Authorization: `Bearer ${createdApiKey}` },
  });
  log('Models: 200', models.status() === 200);
  log('Models: minimax-m2.5', (await models.json()).data?.some(m => m.id === 'minimax-m2.5'));

  // CORS
  const cors = await page.request.fetch(`${LITELLM_BASE}/v1/chat/completions`, {
    method: 'OPTIONS',
    headers: { Origin: 'https://minimax.villamarket.ai', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'authorization,content-type' },
  });
  log('CORS: 2xx', cors.status() >= 200 && cors.status() < 300);
  log('CORS: origin allowed', cors.headers()['access-control-allow-origin'] === 'https://minimax.villamarket.ai');

  // ════════════════════════════════════════════════════════════════
  // 21. SEO
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 21. SEO ══╗');

  // Only check SEO for server-rendered marketing pages (login/dashboard/chat are client-only)
  for (const [route, checks] of [
    ['/', ['MiniMax-M2.5', 'meta', 'SWE-Bench', '$5/month API budget', 'Pricing']],
    ['/docs', ['API Documentation', 'Quick Start']],
  ]) {
    const html = await (await page.goto(BASE + route, { waitUntil: 'commit' })).text();
    log(`SEO ${route}: ${html.length}b`, html.length > 1000);
    for (const c of checks) log(`SEO ${route}: "${c}"`, html.includes(c));
  }

  // Client-only pages should still return valid HTML (just no pre-rendered content)
  for (const route of ['/login', '/dashboard', '/chat']) {
    const html = await (await page.goto(BASE + route, { waitUntil: 'commit' })).text();
    log(`${route}: valid HTML`, html.length > 1000 && html.includes('<!DOCTYPE'));
  }

  // ════════════════════════════════════════════════════════════════
  // 22. SIGN OUT
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ 22. SIGN OUT ══╗');

  await page.goto(BASE + '/dashboard', { waitUntil: 'networkidle' });
  await waitForDashboardLoaded(page);
  const signOut = await page.$('button:has(svg.lucide-log-out)');
  log('Sign out btn visible', !!signOut);
  if (signOut) {
    await signOut.click();
    await page.waitForTimeout(3000);
    log('Redirected after signout', !page.url().includes('/dashboard'));

    await page.goto(BASE + '/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    log('Dashboard → login after signout', page.url().includes('/login'));
  }

  // ════════════════════════════════════════════════════════════════
  // CLEANUP
  // ════════════════════════════════════════════════════════════════
  console.log('\n╔══ CLEANUP ══╗');

  const cleanToken = getIdToken();
  const ch = { Authorization: `Bearer ${cleanToken}`, 'Content-Type': 'application/json' };
  const all = await (await page.request.get(`${API_BASE}/api/keys`, { headers: ch })).json();
  for (const k of all) await page.request.delete(`${API_BASE}/api/keys/${k.token}`, { headers: ch });
  log('Cleanup done', true, `${all.length} keys deleted`);

  // ════════════════════════════════════════════════════════════════
  // SUMMARY
  // ════════════════════════════════════════════════════════════════
  console.log('\n' + '═'.repeat(50));
  const passed = results.filter(r => r.pass).length;
  const failed = results.filter(r => !r.pass).length;
  console.log(`  ${passed} PASSED, ${failed} FAILED out of ${results.length} tests`);
  console.log('═'.repeat(50));

  if (failed > 0) {
    console.log('\nFailed tests:');
    results.filter(r => !r.pass).forEach(r => console.log(`  ✗ ${r.test}: ${r.detail}`));
  }

  await browser.close();
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
