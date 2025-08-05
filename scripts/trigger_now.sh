#!/bin/bash
# Manually trigger the AI news digest function

export PATH="$HOME/google-cloud-sdk/bin:$PATH"
PROJECT_ID="slack-ai-news-feed"

echo "🚀 Manually triggering AI News Digest..."

# Publish message to trigger the function
gcloud pubsub topics publish ai-news-trigger \
    --message='{"trigger":"manual"}' \
    --project="$PROJECT_ID"

echo "✅ Function triggered! Check your Slack channel in a few moments."