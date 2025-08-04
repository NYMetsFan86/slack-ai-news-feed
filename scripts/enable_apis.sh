#!/bin/bash
# Enable all required Google Cloud APIs

echo "🔌 Enabling Google Cloud APIs..."
echo "This may take a few minutes..."

PROJECT_ID="slack-ai-news-feed"
gcloud config set project "$PROJECT_ID"

# Enable all required APIs
gcloud services enable \
    cloudfunctions.googleapis.com \
    cloudscheduler.googleapis.com \
    pubsub.googleapis.com \
    cloudbuild.googleapis.com \
    appengine.googleapis.com \
    firestore.googleapis.com \
    run.googleapis.com \
    eventarc.googleapis.com \
    --project="$PROJECT_ID"

echo ""
echo "✅ APIs enabled! You can now run: ./deploy_auto.sh"