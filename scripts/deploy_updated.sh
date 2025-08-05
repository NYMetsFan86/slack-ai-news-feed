#!/bin/bash
# Deploy updated configuration with The Neuron feed

PROJECT_ID="slack-ai-news-feed"

echo "🚀 Deploying updated AI News Digest with The Neuron feed..."
echo ""

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
gcloud config set project "$PROJECT_ID" 2>/dev/null

# Deploy the function
echo "Deploying Cloud Function..."
gcloud functions deploy ai-news-summarizer \
    --source=. \
    --trigger-topic=ai-news-trigger \
    --runtime=python311 \
    --entry-point=main_function_digest \
    --memory=512MB \
    --timeout=540s \
    --region=us-central1 \
    --set-env-vars="ENVIRONMENT=production,FIRESTORE_COLLECTION=processed_items,OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY .env.gcp | cut -d= -f2),SLACK_WEBHOOK_URL=$(grep SLACK_WEBHOOK_URL .env.gcp | cut -d= -f2),GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "Next steps:"
    echo "1. Update schedule to 8 AM CT: ./scripts/update_schedule_ct.sh"
    echo "2. Trigger manually now: ./scripts/manual_trigger.sh"
else
    echo ""
    echo "❌ Deployment failed"
    echo "Check the error messages above"
fi