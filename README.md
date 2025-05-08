# Podcast RSS Filter Service

A lightweight Flask-based microservice to fetch, filter, and customize Patreon podcast RSS feeds by show name.

## Features

* **Fetch Master Feed**: Retrieves the full RSS feed for a given Patreon podcast slug using your `auth_key`.
* **Filter by Show**: Splits episodes into separate feeds based on regex-defined show names (e.g., `Retro Warriors`, `Retro Warriors Uncut`, `Talking Wizards`, `Read Along`).
* **Miscellaneous Bucket**: Groups any episodes that don’t match defined patterns into a `Miscellaneous` feed.
* **Custom Cover Art**: Optionally override the podcast cover art (`<itunes:image>`) in the channel metadata with your own image URL.
* **RESTful API**: Exposes a single `/rss` endpoint for easy integration or serverless deployment.

## Requirements

* Python 3.7+
* Dependencies listed in `requirements.txt`:

  ```text
  Flask
  requests
  ```

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/bdelcamp/retro-feeds.git
   cd retro-feeds
   ```

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the service locally on port 5000:

```bash
python app.py
```

### Endpoint: `/rss`

#### Query Parameters

| Parameter   | Required | Description                                                    |
| ----------- | -------- | -------------------------------------------------------------- |
| `auth_key`  | Yes      | Your Patreon API auth key.                                     |
| `slug`      | Yes      | The podcast slug (e.g., `retrowarriors`).                      |
| `show`      | No       | The show name to filter (e.g., `Retro Warriors`).              |
| `image_url` | No       | URL to override the podcast cover art in the channel metadata. |

#### Responses

* **List Available Feeds** (no `show` parameter)

  ```json
  {
    "available_feeds": [
      "Retro Warriors",
      "Retro Warriors Uncut",
      "Talking Wizards",
      "Read Along",
      "Miscellaneous"
    ]
  }
  ```

* **Filtered RSS** (with `show` parameter)

  * Content-Type: `application/rss+xml`
  * Body: RSS XML containing only the episodes for the requested show (or `Miscellaneous`).

#### Examples

* **List feeds**

  ```bash
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=retrowarriors"
  ```

* **Fetch specific show**

  ```bash
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=retrowarriors&show=Talking%20Wizards"
  ```

* **Fetch with custom cover art**

  ```bash
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=retrowarriors&show=Read%20Along&image_url=https://example.com/cover.jpg"
  ```

## Configuration

To support additional podcasts, update the `show_patterns_map` in `app.py`:

```python
show_patterns_map = {
    'retrowarriors': {
        'Retro Warriors':       r'^Retro Warriors(?! Uncut)',
        'Retro Warriors Uncut': r'^Retro Warriors Uncut',
        'Talking Wizards':      r'^Talking Wizards',
        'Read Along':           r'^Read Along',
    },
    'anotherpodcast': {
        'Episode A':           r'^Episode A',
        'Special Segment':     r'^Special Segment',
    },
}
```

## Deployment

This service can run on any WSGI-compatible host. For serverless deployments, consider:

* **AWS Lambda** with Zappa or AWS API Gateway
* **Google Cloud Run** / Cloud Functions
* **Azure Functions** (with HTTP trigger)

Ensure `app.run()` is disabled or guarded when deploying to a serverless environment.

## License

This project is licensed under the GPL 3.0 License. See [LICENSE](LICENSE) for details.

---

Happy podcasting! Feel free to open issues or submit PRs for enhancements.
