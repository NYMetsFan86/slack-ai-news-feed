#!/bin/bash
# Quick redeploy script for fixes

export PATH="$HOME/google-cloud-sdk/bin:$PATH"
PROJECT_ID="slack-ai-news-feed"

echo "🔄 Redeploying function with fixes..."
gcloud functions deploy ai-news-digest \
    --runtime=python311 \
    --trigger-topic=ai-news-trigger \
    --entry-point=main_function_digest \
    --source=. \
    --memory=512MB \
    --timeout=540s \
    --env-vars-file=env-vars.yaml \
    --region=us-central1 \
    --project="$PROJECT_ID" \
    --no-gen2 \
    --quiet

echo ""
echo "✅ Redeployment complete!"
echo ""
echo "Test with: gcloud pubsub topics publish ai-news-trigger --message='test'"