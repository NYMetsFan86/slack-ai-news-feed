#!/bin/bash

# Deploy the Cloud Function with proper environment variables
gcloud functions deploy ai-news-summarizer \
    --source=. \
    --trigger-topic=ai-news-trigger \
    --runtime=python311 \
    --entry-point=main_function_digest \
    --memory=512MB \
    --timeout=540s \
    --region=us-central1 \
    --set-env-vars="ENVIRONMENT=production,FIRESTORE_COLLECTION=processed_items,OPENROUTER_API_KEY=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,SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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,GOOGLE_CLOUD_PROJECT=slack-ai-news-feed" \
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