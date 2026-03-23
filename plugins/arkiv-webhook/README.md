# arkiv-webhook

Webhook route plugin for [Arkiv](https://github.com/HerrStolzier/lotse). Sends classified items to any webhook URL — Slack, Discord, n8n, Zapier, or custom endpoints.

## Installation

```bash
pip install arkiv-webhook
```

## Configuration

Add webhook routes to your `~/.config/arkiv/config.toml`:

```toml
# Send all invoices to a Slack channel
[routes.slack-rechnungen]
type = "webhook"
url = "https://hooks.slack.com/services/T.../B.../xxx"
categories = ["rechnung", "vertrag"]
confidence_threshold = 0.7

# Forward articles to n8n workflow
[routes.n8n-articles]
type = "webhook"
url = "http://localhost:5678/webhook/arkiv-articles"
categories = ["artikel", "tutorial"]
confidence_threshold = 0.5

# Send everything to a custom endpoint
[routes.catchall]
type = "webhook"
url = "https://my-api.example.com/arkiv/ingest"
categories = []  # empty = matches all categories
confidence_threshold = 0.3
```

## Webhook Payload

The plugin sends a JSON POST request:

```json
{
  "event": "item_routed",
  "item": {
    "original_path": "/path/to/file.pdf",
    "category": "rechnung",
    "confidence": 0.95,
    "summary": "Telekom Rechnung März 2026",
    "tags": ["telekom", "rechnung"],
    "language": "de",
    "route_name": "slack-rechnungen"
  },
  "timestamp": "2026-03-18T14:30:00+00:00"
}
```

## Notification Formats

The plugin auto-detects Slack and Discord URLs and formats messages accordingly:

- **Slack**: Rich message with category badge and summary
- **Discord**: Embed with color-coded category
- **Generic**: Plain JSON POST to any URL

## License

MIT
