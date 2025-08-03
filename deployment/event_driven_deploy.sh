#!/bin/bash
# Deploy event-driven AI News Summarizer to Google Cloud Platform

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION="us-central1"
PODCAST_CHECK_TOPIC="podcast-check-trigger"
DIGEST_TOPIC="digest-generation-trigger"

echo "🚀 Deploying Event-Driven AI News Summarizer..."

# Create Pub/Sub topics
echo "📬 Creating Pub/Sub topics..."
gcloud pubsub topics create ${PODCAST_CHECK_TOPIC} --project=${PROJECT_ID} || echo "Topic already exists"
gcloud pubsub topics create ${DIGEST_TOPIC} --project=${PROJECT_ID} || echo "Topic already exists"

# Deploy the podcast checker function (lightweight, runs frequently)
echo "🎙️ Deploying podcast checker function..."
gcloud functions deploy podcast-checker \
  --runtime=python311 \
  --trigger-topic=${PODCAST_CHECK_TOPIC} \
  --entry-point=podcast_check_function \
  --source=src/ \
  --memory=128MB \
  --timeout=60s \
  --env-vars-file=.env \
  --region=${REGION} \
  --project=${PROJECT_ID}

# Deploy the main digest generator (runs when triggered)
echo "📰 Deploying digest generator function..."
gcloud functions deploy ai-news-digest \
  --runtime=python311 \
  --trigger-topic=${DIGEST_TOPIC} \
  --entry-point=event_driven_function \
  --source=src/ \
  --memory=512MB \
  --timeout=540s \
  --env-vars-file=.env \
  --region=${REGION} \
  --project=${PROJECT_ID}

# Create Cloud Scheduler jobs
echo "⏰ Setting up Cloud Scheduler..."

# Check for new podcasts every 30 minutes
gcloud scheduler jobs create pubsub podcast-checker-schedule \
  --schedule="*/30 * * * *" \
  --time-zone="America/Denver" \
  --topic=${PODCAST_CHECK_TOPIC} \
  --message-body='{"check": "podcasts"}' \
  --location=${REGION} \
  --project=${PROJECT_ID} || echo "Scheduler already exists"

# Backup daily trigger at 8 AM (in case no new podcasts)
gcloud scheduler jobs create pubsub daily-digest-backup \
  --schedule="0 8 * * *" \
  --time-zone="America/Denver" \
  --topic=${DIGEST_TOPIC} \
  --message-body='{"trigger": "scheduled"}' \
  --location=${REGION} \
  --project=${PROJECT_ID} || echo "Scheduler already exists"

echo "✅ Deployment complete!"
echo ""
echo "📊 Your event-driven system will:"
echo "  - Check for new podcasts every 30 minutes"
echo "  - Generate and send a digest when new content is found"
echo "  - Send a daily digest at 8 AM if no new content triggered it"
echo "  - Include the most recent news and podcasts in each digest"
echo ""
echo "🧪 To test manually:"
echo "  gcloud pubsub topics publish ${PODCAST_CHECK_TOPIC} --message='test'"
echo "  gcloud pubsub topics publish ${DIGEST_TOPIC} --message='test'"