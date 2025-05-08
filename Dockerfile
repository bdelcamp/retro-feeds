# ─────── Build Stage ───────
FROM python:3.13-slim AS builder
# Set up build deps (if you had any C-extensions)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# ─────── Final Stage ───────
FROM python:3.13-slim
# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY . .

# Drop privileges
USER appuser

# Listen on port 5000
EXPOSE 5000

# Use Gunicorn for concurrency; adjust workers & threads as needed
CMD ["/home/appuser/.local/bin/gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3", "--threads", "2"]