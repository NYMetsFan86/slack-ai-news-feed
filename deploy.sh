#!/bin/bash

# Check if required environment variables are set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable is not set"
    echo "Please set it before running this script:"
    echo "  export OPENROUTER_API_KEY='your-api-key-here'"
    exit 1
fi

if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "Error: SLACK_WEBHOOK_URL environment variable is not set"
    echo "Please set it before running this script:"
    echo "  export SLACK_WEBHOOK_URL='your-webhook-url-here'"
    exit 1
fi

# Deploy the Cloud Function with proper environment variables
gcloud functions deploy ai-news-summarizer \
    --source=. \
    --trigger-topic=ai-news-trigger \
    --runtime=python311 \
    --entry-point=main_function_digest \
    --memory=512MB \
    --timeout=540s \
    --region=us-central1 \
    --set-env-vars="ENVIRONMENT=production,FIRESTORE_COLLECTION=processed_items,OPENROUTER_API_KEY=${OPENROUTER_API_KEY},SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL},GOOGLE_CLOUD_PROJECT=slack-ai-news-feed" \
    --project="slack-ai-news-feed" \
    --quiet

echo "Deployment complete!"
echo ""
echo "To trigger manually, run:"
echo "gcloud pubsub topics publish ai-news-trigger --message='{\"test\":true}'"
echo ""
echo "Configuration:"
echo "- 11 news feeds"
echo "- 4 podcast feeds"  
echo "- Up to 8 news items + 3 podcasts per digest"
echo "- AI tip and tool spotlight included"