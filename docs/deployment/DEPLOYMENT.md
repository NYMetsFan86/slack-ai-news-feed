# AI News Summarizer - Deployment Guide

## Prerequisites

Before deploying the AI News Summarizer, ensure you have:

1. **Google Cloud Platform Account** with appropriate permissions to create:
   - Cloud Functions
   - Firestore databases
   - Cloud Scheduler jobs
   - Cloud Logging and monitoring
   - IAM service accounts

2. **Google Cloud SDK (gcloud)** installed and configured with credentials
3. **Google Cloud Build** or **Terraform** (for deployment)
4. **Python 3.11+** installed locally
5. **OpenRouter API Key** from [OpenRouter](https://openrouter.ai/)
6. **Slack Webhook URL** from your Slack workspace

## Configuration

### 1. OpenRouter Setup

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Generate an API key
3. Verify that `meta-llama/llama-3.1-8b-instruct:free` is available in the free tier

### 2. Slack Webhook Setup

1. Go to your Slack workspace
2. Navigate to Apps → Incoming Webhooks
3. Create a new webhook for your desired channel
4. Copy the webhook URL

### 3. Environment Variables

Create a `.env` file for local testing:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
GCP_REGION=us-central1
FIRESTORE_COLLECTION=ai-news-processed-items
ENVIRONMENT=development
```

## Deployment Steps

### 1. Build the Cloud Function Package

```bash
cd deployment
./build_function_package.sh
```

This creates `function_deployment.zip` in the deployment directory.

### 2. Deploy with Google Cloud

```bash
# From the deployment directory
gcloud functions deploy ai-news-summarizer \
  --runtime python311 \
  --trigger-http \
  --entry-point handler \
  --memory 512MB \
  --timeout 300s \
  --set-env-vars OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY,SLACK_WEBHOOK_URL=YOUR_SLACK_WEBHOOK_URL,FIRESTORE_COLLECTION=ai-news-processed-items \
  --source .
```

### 3. Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Create Firestore Database:**
   ```bash
   # Enable Firestore API
   gcloud services enable firestore.googleapis.com
   
   # Create Firestore database (if not exists)
   gcloud firestore databases create --location=us-central1
   ```

2. **Create Cloud Function:**
   ```bash
   gcloud functions deploy ai-news-summarizer \
     --runtime python311 \
     --trigger-http \
     --entry-point handler \
     --memory 512MB \
     --timeout 300s \
     --service-account YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com \
     --source . \
     --set-env-vars OPENROUTER_API_KEY=YOUR_KEY,SLACK_WEBHOOK_URL=YOUR_URL,FIRESTORE_COLLECTION=ai-news-processed-items
   ```

3. **Create Cloud Scheduler Job:**
   ```bash
   # Enable Cloud Scheduler API
   gcloud services enable cloudscheduler.googleapis.com
   
   # Create scheduler job
   gcloud scheduler jobs create http ai-news-summarizer-daily \
     --location=us-central1 \
     --schedule="0 7 * * MON-FRI" \
     --time-zone="America/Denver" \
     --uri="https://REGION-PROJECT_ID.cloudfunctions.net/ai-news-summarizer" \
     --http-method=GET
   ```

## Testing

### Local Testing

```bash
# Install dependencies locally
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Test the Cloud Function handler locally
python -m src.function_handler
```

### GCP Testing

Invoke the Cloud Function manually:

```bash
gcloud functions call ai-news-summarizer \
  --data '{}'
```

## Monitoring

### Cloud Logging

View logs in the GCP Console:
1. Navigate to Cloud Logging → Logs Explorer
2. Filter by `resource.type="cloud_function"` and `resource.labels.function_name="ai-news-summarizer"`
3. View recent log entries

Or use gcloud CLI:
```bash
gcloud functions logs read ai-news-summarizer --limit 50
```

### Cloud Monitoring Alerts

The deployment creates two alerts:
- **ai-news-summarizer-errors**: Triggers on Cloud Function errors
- **ai-news-summarizer-duration**: Triggers if execution exceeds 4 minutes

### Slack Notifications

The Cloud Function sends error notifications to Slack when critical errors occur.

## Maintenance

### Updating the Function

1. Make code changes
2. Rebuild the package:
   ```bash
   ./deployment/build_function_package.sh
   ```
3. Update the function:
   ```bash
   gcloud functions deploy ai-news-summarizer \
     --source deployment/
   ```

### Changing the Schedule

Update the Cloud Scheduler job:
```bash
gcloud scheduler jobs update http ai-news-summarizer-daily \
  --schedule="NEW_CRON_EXPRESSION"
```

### Managing Costs

1. **Firestore**: Uses automatic scaling with pay-per-operation
2. **Cloud Functions**: 
   - Free tier: 2M invocations/month, 400,000 GB-seconds, 200,000 GHz-seconds
   - Optimize memory allocation based on Cloud Monitoring metrics
3. **OpenRouter**: Using free tier models
4. **Cloud Logging**: 
   - Logs retention set to 30 days
   - Consider reducing for cost savings

### Troubleshooting

Common issues and solutions:

1. **Cloud Function Timeout**
   - Check Cloud Logging for slow operations
   - Increase timeout in deployment command if needed

2. **OpenRouter API Errors**
   - Verify API key is correct
   - Check if model is still available in free tier
   - Monitor rate limits

3. **Slack Posting Failures**
   - Verify webhook URL is valid
   - Check Slack workspace settings

4. **No Articles Found**
   - RSS feeds may be down
   - Check if articles are older than 24 hours
   - Verify RSS feed URLs are current

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use Google Secret Manager** for production deployments
3. **Rotate API keys** regularly
4. **Monitor Cloud Logging** for suspicious activity
5. **Use least-privilege IAM service accounts**

## Support

For issues or questions:
1. Check Cloud Logging first
2. Review error notifications in Slack
3. Verify all API keys and webhooks are valid
4. Check GCP service health dashboard