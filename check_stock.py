#!/usr/bin/env python3
"""
ZiBrand hoodie stock watcher.

Polls the Shopify collection feed and sends a WhatsApp message (via CallMeBot)
the moment any watched hoodie variant flips from "coming soon" (available=false)
to available=true.

State is persisted in state.json so you are only pinged on the *transition*,
not on every run. Standard library only — no pip installs needed.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

# --- Configuration (all overridable via environment variables) ---------------
COLLECTION_URL = os.environ.get(
    "COLLECTION_URL",
    "https://www.zibrand.store/collections/hoodies/products.json?limit=250",
)
STORE_LINK = os.environ.get(
    "STORE_LINK", "https://www.zibrand.store/collections/hoodies"
)
STATE_FILE = os.environ.get("STATE_FILE", "state.json")

# Optional: comma-separated substrings. Only product titles containing one of
# these (case-insensitive) are watched. Empty = watch every hoodie.
# e.g. WATCH_PRODUCTS="DNA,BRUTALITY"
WATCH = [w.strip().lower() for w in os.environ.get("WATCH_PRODUCTS", "").split(",") if w.strip()]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

MAX_LINES = 30  # cap message length if the whole store opens at once
UA = "Mozilla/5.0 (compatible; zibrand-stock-watcher/1.0)"


def fetch_products():
    req = urllib.request.Request(COLLECTION_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("products", [])


def is_watched(product):
    if not WATCH:
        return True
    title = (product.get("title") or "").lower()
    return any(w in title for w in WATCH)


def current_available(products):
    """Return {variant_id: human_label} for every available watched variant."""
    avail = {}
    for p in products:
        if not is_watched(p):
            continue
        for v in p.get("variants", []):
            if v.get("available"):
                key = str(v.get("id"))
                avail[key] = (
                    f"{p.get('title')} — {v.get('title')} ({v.get('price')} EGP)"
                )
    return avail


def load_prev_keys():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f).get("available", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_state(available_keys):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "available": sorted(available_keys),
                "last_checked": time.strftime(
                    "%Y-%m-%d %H:%M:%S UTC", time.gmtime()
                ),
            },
            f,
            indent=2,
        )


def send_telegram(text):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print("[warn] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping send.")
        print("[message that would have been sent]\n" + text)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    ).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", "ignore")[:200]
            print("[telegram]", resp.status, body)
    except Exception as e:  # noqa: BLE001 - never let a send error crash the run
        print("[error] Telegram send failed:", e)


def build_message(newly):
    lines = ["ZiBrand hoodies just opened for order!", ""]
    shown = sorted(newly)
    for lbl in shown[:MAX_LINES]:
        lines.append("- " + lbl)
    if len(shown) > MAX_LINES:
        lines.append(f"...and {len(shown) - MAX_LINES} more")
    lines += ["", "Order now: " + STORE_LINK]
    return "\n".join(lines)


def main():
    products = fetch_products()
    current = current_available(products)
    prev_keys = load_prev_keys()
    newly = [current[k] for k in current if k not in prev_keys]

    print(
        f"Checked {len(products)} products. "
        f"Available variants now: {len(current)}. Newly available: {len(newly)}."
    )

    if newly:
        send_telegram(build_message(newly))

    save_state(set(current.keys()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
