// Plays explainer.html in headless Chromium with audio-synced scene
// durations and records the frame. Captures the REAL wall-clock moment each
// scene appears (via an exposed callback) so the voiceover can be aligned to
// the actual recording. Output: out/*.webm + out/timeline.json
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
  await context.addInitScript((d) => { window.__durations = d; }, durations);

  const page = await context.newPage();
  const t0 = Date.now(); // ~ recording start

  const timeline = {};
  await page.exposeFunction('__onScene', (idx) => {
    if (timeline[idx] === undefined) timeline[idx] = Date.now() - t0;
  });

  const url = 'file://' + path.join(process.cwd(), 'explainer.html') + '?record=1';
  console.log('Opening', url);
  await page.goto(url, { waitUntil: 'load' });

  await page.waitForTimeout(1300); // let web fonts settle
  await page.evaluate(() => window.__startStory());

  await page
    .waitForFunction(() => window.__storyDone === true, null, { timeout: 200000 })
    .catch(() => console.log('story-done flag not seen; closing anyway'));

  await page.waitForTimeout(900);
  await context.close(); // finalizes the video file
  await browser.close();

  const arr = [];
  for (let i = 0; i < durations.length; i++) arr.push(timeline[i] !== undefined ? timeline[i] : null);
  fs.writeFileSync('out/timeline.json', JSON.stringify(arr));
  console.log('timeline(ms from recording start) =', arr);
})();
