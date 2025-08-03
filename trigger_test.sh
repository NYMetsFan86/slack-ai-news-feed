#!/bin/bash

# Test trigger for AI News Digest

echo "🚀 Triggering AI News Digest Test..."
echo "=================================="

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "🎯 Triggering function via Pub/Sub..."

# Publish test message to trigger the function
gcloud pubsub topics publish ai-news-trigger \
    --message='{"test": true, "source": "manual_trigger"}' \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo "✅ Test trigger sent successfully!"
    echo ""
    echo "📊 Check your Slack channel in ~30-60 seconds"
    echo "📝 To view logs, run:"
    echo "   gcloud functions logs read ai-news-digest --region=us-central1 --limit=50"
else
    echo "❌ Failed to send trigger"
fi