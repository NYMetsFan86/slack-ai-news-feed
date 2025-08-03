#!/bin/bash

# Deploy to Google Cloud Functions
# This script deploys the AI News Summarizer to GCP

set -e

echo "🚀 Deploying AI News Summarizer to Google Cloud Platform..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | xargs)
fi

# Check required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT not set in .env file"
    exit 1
fi

# Set the project
echo "📋 Setting GCP project to: $GOOGLE_CLOUD_PROJECT"
gcloud config set project "$GOOGLE_CLOUD_PROJECT"

# Create Pub/Sub topic if it doesn't exist
echo "📬 Creating Pub/Sub topic..."
gcloud pubsub topics create ai-news-trigger 2>/dev/null || echo "Topic already exists"

# Deploy the Cloud Function
echo "☁️ Deploying Cloud Function..."
cd "$PROJECT_ROOT"

gcloud functions deploy ai-news-summarizer \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=main_function \
    --trigger-topic=ai-news-trigger \
    --memory=512MB \
    --timeout=540s \
    --env-vars-file=.env \
    --service-account=ai-news-summarizer@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --max-instances=1

# Create Cloud Scheduler job
echo "⏰ Creating Cloud Scheduler job..."

# Check if Cloud Scheduler API is enabled
gcloud services enable cloudscheduler.googleapis.com 2>/dev/null || true

# Create the scheduler job (7 AM MST = 2 PM UTC)
gcloud scheduler jobs create pubsub ai-news-daily \
    --location=us-central1 \
    --schedule="0 14 * * 1-5" \
    --time-zone="UTC" \
    --topic=ai-news-trigger \
    --message-body='{"trigger":"scheduled"}' \
    --description="Daily AI news summarizer trigger" 2>/dev/null || \
    echo "Scheduler job already exists (updating instead)" && \
    gcloud scheduler jobs update pubsub ai-news-daily \
        --location=us-central1 \
        --schedule="0 14 * * 1-5" \
        --time-zone="UTC"

echo "✅ Deployment complete!"
echo ""
echo "📊 Next steps:"
echo "1. Test manually: gcloud pubsub topics publish ai-news-trigger --message='{\"test\":true}'"
echo "2. View logs: gcloud functions logs read ai-news-summarizer --limit=50"
echo "3. Check Slack channel for messages"
echo ""
echo "🎉 Your AI News Summarizer is now live on Google Cloud Platform!"