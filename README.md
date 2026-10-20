# PricePhoenix

A GitHub Actions-powered product price tracker starter for Amazon India and Flipkart.

## What works in this starter

- Products are configured in `config/products.json`.
- Mock mode lets you test the complete pipeline without contacting marketplaces.
- Price history is stored in CSV.
- Recommendation rules are deterministic and testable.
- Email alerts can be sent through Gmail SMTP.
- GitHub Actions supports manual runs and a six-hour schedule.
- Adapter interfaces are separated from the tracker so official/authorized data sources can be added independently.

## Important limitation

The Amazon and Flipkart adapters are intentionally safe placeholders. Real marketplace access must be configured using an API or other permitted data source for which you have access. Do not assume a marketplace API account will automatically be eligible. Do not put credentials in JSON or source code.

## Quick start locally

Requirements: Python 3.11+

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m src.main --mock
pytest -q
```

Mock mode uses `mock_prices.json` and does not contact Amazon or Flipkart. It will write `data/price_history.csv` and print any alert decisions.

## Configure products

Edit `config/products.json`. Use actual product URLs and your own target prices. The example URLs are placeholders.

- `target_price`: desired buying price, INR.
- `alert_threshold`: optional price at which a near-target alert may be triggered.
- `enabled`: set false to pause tracking.
- `source`: `amazon`, `flipkart`, or `mock`.

For now, use `"source": "mock"` for reliable testing. Marketplace adapters return a clear configuration error until a permitted API integration is implemented.

## Gmail setup

1. Enable 2-Step Verification on the Google account, if eligible.
2. Create an app password in Google Account security settings.
3. In GitHub repository settings, add Actions secrets:
   - `SMTP_USERNAME` = Gmail address
   - `SMTP_APP_PASSWORD` = app password
   - `ALERT_TO_EMAIL` = recipient address
4. Keep secrets out of files and logs.

Email is disabled unless these secrets are present and `EMAIL_ENABLED` is set to `true`.

## GitHub Actions setup

1. Create a GitHub repository and upload these files.
2. In Settings → Secrets and variables → Actions, add the three secrets above.
3. Enable Actions for the repository.
4. Open Actions → `PricePhoenix` → Run workflow for a manual test.
5. The workflow also runs every six hours (UTC), subject to GitHub's schedule delays and usage limits.

The workflow commits price history back to the repository. It only commits when the history file changes. If you prefer not to allow workflow write access, change persistence to an artifact or external store instead.

## Tests

```bash
pytest -q
```

Tests cover configuration validation, recommendation rules, and alert deduplication without needing real marketplace requests.

## Roadmap

1. Verify this mock-mode starter and tests.
2. Confirm Amazon and Flipkart data-source access.
3. Implement one adapter at a time and validate returned prices against the product pages.
4. Add product availability, cross-marketplace matching, daily digest, and more historical analysis.
