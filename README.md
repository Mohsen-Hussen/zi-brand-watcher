# ZiBrand hoodie stock watcher

Watches the [ZiBrand hoodies collection](https://www.zibrand.store/collections/hoodies)
and sends you a **WhatsApp message the moment a hoodie opens for order** (when it
stops being "coming soon"). Runs for free in the cloud via GitHub Actions — your
PC can be off.

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

### 1. Set up CallMeBot WhatsApp (you must do this — it's tied to your phone)

1. Save this phone number to your contacts: **+34 621 331 709** (CallMeBot).
2. From your WhatsApp, send it this exact message: **`I allow callmebot to send me messages`**
3. You'll get a reply with your personal **API key** (a number). Keep it.
   - Your phone number for the next step is in international format with no `+`,
     e.g. Egypt mobile `01012345678` → `201012345678`.

Docs: https://www.callmebot.com/blog/free-api-whatsapp-messages/

### 2. Put the code on GitHub

Create a new repository (can be private) and push this folder to it. With the
GitHub CLI:

```powershell
gh repo create zi-brand-watcher --private --source . --remote origin --push
```

Or create the repo on github.com and follow its "push an existing repository"
instructions.

### 3. Add your WhatsApp secrets to the repo

In the GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**.
Add two secrets:

| Name | Value |
|---|---|
| `CALLMEBOT_PHONE` | your number in international format, no `+` (e.g. `201012345678`) |
| `CALLMEBOT_APIKEY` | the API key CallMeBot sent you |

*(Optional)* To watch only specific hoodies instead of all of them, add a
repository **variable** (not secret) named `WATCH_PRODUCTS`, e.g. `DNA,BRUTALITY`.

### 4. Turn it on

Open the repo's **Actions** tab, enable workflows if prompted, pick
**ZiBrand stock watcher**, and click **Run workflow** once to test. Check the run
log — it prints how many products it saw. Since everything is "coming soon" now,
you won't get a message yet; you will the moment a hoodie opens.

---

## Test the WhatsApp alert works

Trigger one run manually (step 4). To force a test message, you can temporarily
edit `state.json`'s `last_checked` — but the cleanest test is to confirm the run
log shows `Checked N products` with no errors, which means the feed fetch and
state logic work. The WhatsApp path is exercised automatically on the first real
transition.

## Run locally (optional)

Requires Python 3 (the cloud runner already has it; Windows may not).

```powershell
$env:CALLMEBOT_PHONE="201012345678"; $env:CALLMEBOT_APIKEY="123456"; python3 check_stock.py
```

## Tuning

- **Frequency:** edit the `cron` in `.github/workflows/stock-check.yml`
  (`*/5 * * * *` = every 5 min; GitHub's minimum for scheduled jobs).
- **Which hoodies:** set the `WATCH_PRODUCTS` repo variable.

## Not using CallMeBot?

CallMeBot is a free community relay — fine for personal alerts. For something
more robust you can swap `send_whatsapp()` in `check_stock.py` for Twilio's
WhatsApp API (needs a Twilio account and credentials).
