# Retro Feeds

A lightweight Flask-based microservice to fetch, filter, and customize Patreon podcast RSS feeds by show name.
> [!NOTE] Wik
>
> This has literally only been tested / used for the Retro Warriors Podcast, as it's the only one I subscribe to on Patreon. So YMMV with other shows. It should be easily extensible.

> [!NOTE] Also Wik
>
> If you plan on self hosting this, please use a vpn like Tailscale or something. If you MUST expose it over the interwebs, use a reverse proxy with SSL as to not expose your patreon key to MITM attacks.

> [!NOTE] Also Also Wik
>
> If someone is MITM'ing you're stuff, you probably have an extensive patreon support list, or you have other things to worry about.

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
| `auth_key`  | Yes      | Your Patreon API auth key. Only required if [PATREON_AUTH_KEY environment variable](#environment-variables) is not set. If both are provided, the query parameter is the dominant option.                                     |
| `slug`      | Yes      | The podcast slug (e.g., `Retro Warriors`).                      |
| `show`      | No       | The show name to filter (e.g., `Read Along`).              |
| `image_url` | No       | URL to override the podcast cover art in the channel metadata. |

#### Responses

* **List Available Feeds** (no `show` parameter)

  ```json
  {
    "available_feeds": [
      "Main",
      "Uncut",
      "Read Along",
      ...
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
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=Retro%20Warriors"
  ```

* **Fetch specific show**

  ```bash
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=Retro%20Warriors&show=Talking%20Wizards"
  ```

* **Fetch with custom cover art**

  ```bash
  curl "http://localhost:5000/rss?auth_key=YOUR_KEY&slug=Retro%20Warriors&show=Read%20Along&image_url=https://example.com/cover.jpg"
  ```

## Configuration

To support additional podcasts, update the `show_patterns_map` in `app.py`:

```python
show_patterns_map = {
    'Retro Warriors': {
            'Main': r'Retro Warriors(?! Uncut)',
            'Uncut': r'Uncut',
            'Talking Wizards': r'Talking Wizard',
            'Read Along': r'Read Along',
            'Cinema Rogues': r'^Cinema Rogues',
            'Classic Corner': r'Classic Corner',
        },
    'anotherpodcast': {
        'Episode A':           r'^Episode A',
        'Special Segment':     r'^Special Segment',
    },
}
```

### Environment Variables

| Variable   | Description                                                    |
| ---------- | ------------------------------------------------------------- |
| `PATREON_AUTH_KEY` | Define this if you will be personally only accessing this instance. It will not be required in the request URL. |
|`APP_PORT` | Overrides the port the application is served on. |
|`DEBUG` | Sets the debug mode on the local flask server if you're testing. |

## Deployment

This service can run on any WSGI-compatible host. For serverless deployments, consider:

* **AWS Lambda** with Zappa or AWS API Gateway
* **Google Cloud Run** / Cloud Functions
* **Azure Functions** (with HTTP trigger)

Ensure `app.run()` is disabled or guarded when deploying to a serverless environment.

### Docker

Included docker compose. Running a `docker compose up` will build the image if necessary, and then start it with default options. Add environment variables to your liking to the compose file, or a .env

## License

This project is licensed under the GPL 3.0 License. See [LICENSE](LICENSE) for details.

---

Happy podcasting! Feel free to open issues or submit PRs for enhancements.
