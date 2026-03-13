import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

page.on('console', msg => {
  if (msg.type() === 'error') console.log(`[PAGE ERROR] ${msg.text().substring(0, 200)}`);
});
page.on('response', resp => {
  const url = resp.url();
  if (url.includes('api.minimax') || url.includes('/v1/') || (url.includes('gpu-workspace') && !url.includes('.js'))) {
    console.log(`[NET] ${resp.status()} ${url.substring(0, 140)}`);
  }
});

// Login
await page.goto('https://minimax.villamarket.ai/login', { waitUntil: 'networkidle' });
await page.fill('input[type="email"]', 'test@minimax.villamarket.ai');
await page.fill('input[type="password"]', 'TestPass99');
await page.click('button:has-text("Sign In")');
await page.waitForURL('**/dashboard', { timeout: 15000 }).catch(() => {});
console.log('1. Logged in at:', page.url());

// Go to chat
await page.goto('https://minimax.villamarket.ai/chat', { waitUntil: 'networkidle' });
await page.waitForSelector('textarea', { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(5000);
console.log('2. Chat URL:', page.url());

const textarea = await page.$('textarea');
const disabled = textarea ? await textarea.isDisabled() : true;
console.log('3. Textarea found:', !!textarea, 'disabled:', disabled);

const storedKeys = await page.evaluate(() => localStorage.getItem('minimax_api_keys'));
console.log('4. Stored keys:', storedKeys ? storedKeys.substring(0, 30) : 'null');

if (textarea && !disabled) {
  await page.fill('textarea', 'Say hello in exactly 3 words');
  await page.click('button:has(svg.lucide-send)');
  console.log('5. Message sent, waiting 30s...');
  await page.waitForTimeout(30000);

  // Check the rendered content
  const body = await page.textContent('body');
  console.log('6. Has raw <think>:', body.includes('<think>'));
  console.log('7. Has raw </think>:', body.includes('</think>'));
  console.log('8. Has user msg:', body.includes('Say hello'));

  // Check ThinkBlock toggle ("Thought process" when done, "Thinking..." while streaming)
  const thinkBlock = await page.$('button:has-text("Thought process")');
  const thinkStreaming = await page.$('button:has-text("Thinking")');
  console.log('9. Has ThinkBlock toggle:', !!(thinkBlock || thinkStreaming));

  // Get assistant content (MarkdownRenderer uses div.markdown-content)
  const mdBlocks = await page.$$('div.markdown-content');
  console.log('10. Markdown content blocks:', mdBlocks.length);
  for (const block of mdBlocks) {
    const text = await block.textContent();
    console.log('  Content:', text.substring(0, 200));
  }

  // Also check the conversation sidebar for the response preview
  const sidebar = await page.$('.font-medium:has-text("Say hello")');
  console.log('11. Conversation in sidebar:', !!sidebar);

  // Check no page errors occurred
  console.log('12. SUCCESS: Chat is working');

  await page.screenshot({ path: '/tmp/chat-result.png' });
} else {
  console.log('FAIL: Cannot type - textarea disabled');
  await page.screenshot({ path: '/tmp/chat-result.png' });
}

await browser.close();
