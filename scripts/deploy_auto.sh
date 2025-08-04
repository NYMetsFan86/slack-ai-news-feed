#!/bin/bash
# Automated deployment script (non-interactive)

set -e

echo "🚀 AI News Summarizer - Automated Deployment"
echo "==========================================="

# Add gcloud to PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Set project
PROJECT_ID="slack-ai-news-feed"
gcloud config set project "$PROJECT_ID"

# Source clean env file
source .env.gcp

# Check Firestore
echo ""
echo "🗄️ Checking Firestore..."
if gcloud firestore databases describe --database="(default)" &>/dev/null; then
    echo "✅ Firestore (default) database exists"
else
    echo "Creating Firestore database..."
    gcloud firestore databases create --location=us-central1 --database="(default)"
fi

# Enable APIs
echo ""
echo "🔌 Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com pubsub.googleapis.com cloudbuild.googleapis.com appengine.googleapis.com firestore.googleapis.com run.googleapis.com eventarc.googleapis.com --quiet

# Create topics
echo ""
echo "📬 Creating Pub/Sub topic..."
gcloud pubsub topics create ai-news-trigger --quiet 2>/dev/null || echo "Topic already exists"

# Deploy the digest function
echo ""
echo "🚀 Deploying Cloud Function (digest version)..."
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

# Create scheduler job for weekdays at 8 AM MST
echo ""
echo "⏰ Creating Cloud Scheduler job..."
gcloud scheduler jobs create pubsub ai-news-daily \
    --schedule="0 8 * * 1-5" \
    --time-zone="America/Denver" \
    --topic=ai-news-trigger \
    --message-body='{"trigger":"scheduled"}' \
    --location=us-central1 \
    --project="$PROJECT_ID" \
    --quiet 2>/dev/null || echo "Scheduler job already exists"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Next steps:"
echo "1. Test manually:"
echo "   gcloud pubsub topics publish ai-news-trigger --message='test'"
echo ""
echo "2. View logs:"
echo "   gcloud functions logs read ai-news-digest --limit=50"
echo ""
echo "3. Cloud Console:"
echo "   https://console.cloud.google.com/functions/details/us-central1/ai-news-digest?project=$PROJECT_ID"