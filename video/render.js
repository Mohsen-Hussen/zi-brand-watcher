// Plays explainer.html in headless Chromium with audio-synced scene
// durations, records the frame, and reports the pre-roll so the narration
// can be aligned. Output: out/*.webm + out/preroll.json
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const durations = JSON.parse(fs.readFileSync('durations.json', 'utf8')); // ms per scene
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: 'out', size: { width: 1920, height: 1080 } },
  });
  // inject durations before any page script runs
  await context.addInitScript((d) => { window.__durations = d; }, durations);

  const page = await context.newPage();
  const t0 = Date.now(); // ~ recording start

  const url = 'file://' + path.join(process.cwd(), 'explainer.html') + '?record=1';
  console.log('Opening', url);
  await page.goto(url, { waitUntil: 'load' });

  await page.waitForTimeout(1300); // let web fonts settle
  const startAt = Date.now();
  await page.evaluate(() => window.__startStory());
  const preroll = startAt - t0;
  console.log('preroll(ms)=', preroll);

  await page
    .waitForFunction(() => window.__storyDone === true, null, { timeout: 160000 })
    .catch(() => console.log('story-done flag not seen; closing anyway'));

  await page.waitForTimeout(900);
  await context.close(); // finalizes the video file
  await browser.close();

  fs.writeFileSync('out/preroll.json', JSON.stringify({ preroll_ms: preroll }));
  console.log('render complete');
})();
