# ZiBrand hoodie stock watcher

Watches the [ZiBrand hoodies collection](https://www.zibrand.store/collections/hoodies)
and sends you a **Telegram message the moment a hoodie opens for order** (when it
stops being "coming soon"). Runs for free in the cloud via GitHub Actions — your
PC can be off.

> Originally planned for WhatsApp, but the free CallMeBot relay closed new
> signups, so this uses Telegram instead — free, instant, and far more reliable.

## How it works

The store runs on Shopify, which exposes a public feed at
`.../collections/hoodies/products.json`. Every size/color variant has an
`"available"` flag that is currently `false` for all hoodies (that's the "coming
soon" state). The watcher polls that feed every ~5 minutes and messages you the
instant any variant flips to `true`. A small `state.json` remembers what was
already open, so you're pinged only on the change — not every run.

> It only **notifies** you. It does not auto-buy — you place the order yourself,
> which is both safer and more reliable.

---

## Setup (one-time, ~10 minutes)

### 1. Create a Telegram bot and get your chat ID (you must do this)

1. In Telegram, open a chat with **@BotFather**, send `/newbot`, and follow the
   prompts. It gives you a **bot token** like `123456789:AAE...xyz`. Keep it.
2. Open a chat with **your new bot** and send it any message (e.g. `hi`). This is
   required — a bot can't message you until you've messaged it first.
3. Get your **chat ID**: open a chat with **@userinfobot** and it replies with
   your numeric ID (e.g. `5566778899`). That's your `TELEGRAM_CHAT_ID`.
   - Alternative: after step 2, visit
     `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser and read
     the `"chat":{"id": ...}` value.

Docs: https://core.telegram.org/bots#how-do-i-create-a-bot

### 2. Put the code on GitHub

Create a new repository (can be private) and push this folder to it. With the
GitHub CLI:

```powershell
gh repo create zi-brand-watcher --private --source . --remote origin --push
```

Or create the repo on github.com and follow its "push an existing repository"
instructions.

### 3. Add your Telegram secrets to the repo

In the GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**.
Add two secrets:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | the bot token from @BotFather (e.g. `123456789:AAE...xyz`) |
| `TELEGRAM_CHAT_ID` | your numeric chat ID (e.g. `5566778899`) |

*(Optional)* To watch only specific hoodies instead of all of them, add a
repository **variable** (not secret) named `WATCH_PRODUCTS`, e.g. `DNA,BRUTALITY`.

### 4. Turn it on

Open the repo's **Actions** tab, enable workflows if prompted, pick
**ZiBrand stock watcher**, and click **Run workflow** once to test. Check the run
log — it prints how many products it saw. Since everything is "coming soon" now,
you won't get a message yet; you will the moment a hoodie opens.

---

## Test the alert works

After you've added the `TELEGRAM_BOT_TOKEN` secret:

1. Go to the repo's **Actions** tab → **ZiBrand stock watcher** → **Run workflow**.
2. **Tick the "Send a test Telegram message" box**, then run it.
3. You should get a Telegram message within a few seconds confirming it's wired up.

A normal (unticked) run instead checks stock and logs `Checked N products` —
the real alert fires automatically the moment a hoodie opens for order.

## Run locally (optional)

Requires Python 3 (the cloud runner already has it; Windows may not).

```powershell
$env:TELEGRAM_BOT_TOKEN="123456789:AAE...xyz"; $env:TELEGRAM_CHAT_ID="5566778899"; python3 check_stock.py
```

To confirm Telegram delivery works end-to-end, temporarily put a real variant ID
in `state.json`'s `available` list, run once (you'll get a "newly available"
ping for everything *not* in that list — or just trust the first real run). The
simplest check: a manual workflow run that logs `Checked N products` with no
`[error]` lines means the pipeline is healthy.

## Tuning

- **Frequency:** edit the `cron` in `.github/workflows/stock-check.yml`
  (`*/5 * * * *` = every 5 min; GitHub's minimum for scheduled jobs).
- **Which hoodies:** set the `WATCH_PRODUCTS` repo variable.

## Want WhatsApp instead of Telegram?

Swap the `send_telegram()` function in `check_stock.py` for a WhatsApp provider:
- **CallMeBot** (free) — re-opens signups periodically; was full at build time.
- **TextMeBot** (low cost) — same simple HTTP API as CallMeBot.
- **Twilio WhatsApp** (official) — most robust, needs a Twilio account.
