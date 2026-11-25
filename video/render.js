// Renders explainer.html to a video by playing it in headless Chromium
// and recording the frame. Output: out/*.webm (converted to mp4 in CI).
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: 'out', size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();

  const url = 'file://' + path.join(process.cwd(), 'explainer.html') + '?record=1';
  console.log('Opening', url);
  await page.goto(url, { waitUntil: 'load' });

  // let web fonts settle before the story starts animating
  await page.waitForTimeout(1500);

  // the page sets window.__storyDone = true when the last scene finishes
  // (total scene time is ~67s; wait with a generous margin)
  await page
    .waitForFunction(() => window.__storyDone === true, null, { timeout: 110000 })
    .catch(() => console.log('story-done flag not seen; closing anyway'));

  await page.waitForTimeout(900);
  await context.close(); // finalizes the video file
  await browser.close();
  console.log('render complete');
})();
