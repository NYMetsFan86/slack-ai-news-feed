# Configuration Guide

This guide covers all configuration options for the AI News Summarizer.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | API key from OpenRouter | `sk-or-v1-xxxxx` |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | `https://hooks.slack.com/services/XXX/YYY/ZZZ` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_REGION` | GCP region for deployment | `us-central1` |
| `FIRESTORE_COLLECTION` | Name of Firestore collection | `ProcessedItems` |
| `ENVIRONMENT` | Environment name | `production` |

## RSS Feed Configuration

Edit `src/config.py` to customize RSS feeds:

### Adding News Feeds

```python
NEWS_FEEDS = [
    {
        "name": "Source Name",
        "url": "https://example.com/rss.xml",
        "type": "news"
    }
]
```

### Adding Podcast Feeds

```python
PODCAST_FEEDS = [
    {
        "name": "Podcast Name",
        "url": "https://podcast.com/rss",
        "type": "podcast"
    }
]
```

### Finding Podcast RSS Feeds

#### From Popular Platforms:

1. **Apple Podcasts**
   - Search for the podcast on Apple Podcasts
   - Right-click on the podcast name
   - Select "Copy Link"
   - Use a service like [GetRSSFeed](https://getrssfeed.com/) to extract the RSS

2. **Google Podcasts**
   - Most Google Podcasts have publicly available RSS feeds
   - Search "[podcast name] RSS feed" in Google

3. **Spotify Podcasts**
   - Spotify doesn't provide public RSS feeds for all podcasts
   - If the podcast is hosted elsewhere, search for the original hosting platform
   - Check the podcast's website for RSS links

4. **Direct from Podcast Websites**
   - Look for RSS icon or "Subscribe" links
   - Check footer or about pages
   - Common patterns: `/feed`, `/rss`, `/podcast.xml`

### Example: Adding a Custom Podcast

To add the podcast you mentioned, you would need to:

1. Find if it has an RSS feed outside of Spotify
2. Check the podcast's official website
3. Search for "[podcast name] RSS feed"

If no RSS feed is available, alternatives include:
- Contact the podcast creator for the RSS feed
- Check if they publish on other platforms with RSS
- Use their website's news/updates page if available

## Schedule Configuration

### Default Schedule

The default schedule runs at 7 AM MST (14:00 UTC) on weekdays:

```yaml
ScheduleExpression: 'cron(0 14 ? * MON-FRI *)'
```

### Custom Schedules

Common schedule patterns:

```yaml
# Every weekday at 9 AM EST (14:00 UTC)
ScheduleExpression: 'cron(0 14 ? * MON-FRI *)'

# Every day at 8 AM PST (16:00 UTC)
ScheduleExpression: 'cron(0 16 * * ? *)'

# Twice daily at 7 AM and 3 PM MST
ScheduleExpression: 'cron(0 14,22 ? * MON-FRI *)'

# Every Monday at 7 AM MST
ScheduleExpression: 'cron(0 14 ? * MON *)'
```

### Cron Expression Format

```
cron(Minutes Hours Day-of-month Month Day-of-week Year)
```

- Use `?` for Day-of-month or Day-of-week (not both)
- Use `*` for "every"
- Use `,` for multiple values
- Times are in UTC

## Content Filtering

### Adjusting Summary Length

In `src/config.py`:

```python
SUMMARY_BULLET_POINTS = 5  # Number of bullet points
AI_TIP_MAX_LENGTH = 300   # Maximum characters for tips
```

### Filtering Article Age

In `src/rss_parser.py`:

```python
# Only fetch articles from last 24 hours
hours_back = 24  # Adjust as needed
```

### Maximum Articles Per Feed

```python
MAX_ARTICLES_PER_FEED = 3  # Limit to prevent overwhelming
```

## LLM Configuration

### Model Selection

Current model in `src/config.py`:

```python
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
```

### Alternative Free Models

```python
# Google's Gemma
OPENROUTER_MODEL = "google/gemma-2-9b-it:free"

# Mistral
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"

# Check OpenRouter for current free models
```

### Customizing Prompts

Edit prompts in `src/llm_client.py`:

```python
# For news summaries
system_prompt = """You are an AI news summarizer for a business audience. 
Focus on practical implications and why it matters to professionals."""

# For AI tips
system_prompt = """Generate practical, actionable AI tips for business users.
Keep it under 200 characters and make it specific."""
```

## Security Configuration

### API Key Rotation

1. Generate new keys from providers
2. Update Cloud Function environment variables:
   ```bash
   gcloud functions deploy ai-news-summarizer \
     --update-env-vars OPENROUTER_API_KEY=new-key
   ```

### Network Security

For VPC deployment, add to deployment configuration:

```yaml
vpcConnector: projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME
egressSettings: PRIVATE_RANGES_ONLY
```

## Performance Tuning

### Cloud Function Memory

Adjust in deployment configuration:

```yaml
availableMemoryMb: 512  # MB (128-8192)
```

### Timeout Settings

```yaml
Timeout: 300  # seconds (max 900)
```

### Concurrent Executions

```yaml
ReservedConcurrentExecutions: 1  # Prevent parallel runs
```

## Monitoring Configuration

### Cloud Monitoring Alerts

Add custom alerts in deployment configuration:

```yaml
alerts:
  - displayName: "Your Alert"
    conditions:
      - displayName: "Your Condition"
        conditionThreshold:
          filter: metric.type="cloudfunctions.googleapis.com/function/execution_count"
          threshold: YourThreshold
```

### Log Retention

```yaml
LogGroup:
  Properties:
    RetentionInDays: 30  # Adjust as needed
```

## Testing Configuration

### Local Testing

Create `.env.test`:

```bash
ENVIRONMENT=development
OPENROUTER_API_KEY=test-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/test
```

### Mock Mode

Enable mock mode in `src/config.py`:

```python
# Add to Config class
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
```

Then check in code:

```python
if Config.MOCK_MODE:
    # Return mock data instead of calling APIs
    return mock_response
```