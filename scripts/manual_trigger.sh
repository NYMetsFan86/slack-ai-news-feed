#!/bin/bash
# Manual trigger script that handles authentication

PROJECT_ID="slack-ai-news-feed"

echo "🚀 Manually triggering AI News Digest..."
echo ""

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo "❌ Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID" 2>/dev/null

# Check if the topic exists
echo "Checking if topic exists..."
if ! gcloud pubsub topics describe ai-news-trigger --project="$PROJECT_ID" 2>/dev/null; then
    echo "❌ Topic 'ai-news-trigger' not found"
    echo "Creating topic..."
    gcloud pubsub topics create ai-news-trigger --project="$PROJECT_ID"
fi

# Publish message to trigger function
echo "Publishing trigger message..."
gcloud pubsub topics publish ai-news-trigger \
    --message='{"trigger":"manual","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Function triggered successfully!"
    echo "Check your Slack channel in a few moments."
    echo ""
    echo "To view logs, run:"
    echo "gcloud functions logs read ai-news-summarizer --limit=50"
else
    echo ""
    echo "❌ Failed to trigger function"
    echo "Please check your authentication and project settings"
fi