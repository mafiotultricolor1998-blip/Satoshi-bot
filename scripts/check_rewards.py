import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html import unescape

SOURCES = [
    {
        "name": "Bitcoin Entdecken",
        "url": "https://bitcoin-entdecken.de/",
    },
    {
        "name": "BTC GACHA",
        "url": "https://www.btcgacha.com/",
    },
    {
        "name": "MintSats",
        "url": "https://mintsats.app/",
    },
    {
        "name": "Free Crypto World",
        "url": "https://freecrypto.world/",
    },
    {
        "name": "sMiles",
        "url": "https://www.smilesbitcoin.com/",
    },
    {
        "name": "FreeBitcoin",
        "url": "https://freebitco.in/",
    },
]

KEYWORDS = [
    "reward", "rewards", "faucet", "satoshi",
    "bitcoin", "claim", "free btc", "earn bitcoin",
]

def check_source(source):
    checked_at = datetime.now(timezone.utc).isoformat()
    result = {
        **source,
        "checkedAt": checked_at,
        "accessible": False,
        "httpStatus": None,
        "indicators": [],
        "note": "",
    }

    request = urllib.request.Request(
        source["url"],
        headers={"User-Agent": "SatoshiBot-PublicMonitor/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.status
            html = response.read(1_000_000).decode(
                "utf-8", errors="replace"
            )

        text = unescape(re.sub(r"<[^>]+>", " ", html))
        text = re.sub(r"\s+", " ", text).lower()

        result["accessible"] = 200 <= status < 400
        result["httpStatus"] = status
        result["indicators"] = [
            word for word in KEYWORDS if word in text
        ]
        result["note"] = (
            "Public page checked. Keywords are clues only; "
            "they do not confirm an available reward or payment."
        )

    except Exception as error:
        result["note"] = (
            "Could not verify this page automatically: "
            + type(error).__name__
        )

    return result


def main():
    now = datetime.now(timezone.utc).isoformat()
    report = {
        "checkedAt": now,
        "intervalHours": 6,
        "disclaimer": (
            "Public-page monitoring only. No account login, "
            "eligibility verification, claims, or payments."
        ),
        "sources": [check_source(source) for source in SOURCES],
    }

    output = Path("data/rewards.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Checked {len(SOURCES)} public sources.")
    print(f"Report saved to {output}.")


if __name__ == "__main__":
    main()
