#!/bin/bash
# Update the Cloud Scheduler job to run at 8 AM MST on weekdays only

export PATH="$HOME/google-cloud-sdk/bin:$PATH"
PROJECT_ID="slack-ai-news-feed"

echo "📅 Updating schedule to 8 AM MST on weekdays..."

# Delete existing job
echo "Removing old schedule..."
gcloud scheduler jobs delete ai-news-daily \
    --location=us-central1 \
    --project="$PROJECT_ID" \
    --quiet 2>/dev/null || echo "No existing job to delete"

# Create new job with updated schedule
echo "Creating new schedule..."
gcloud scheduler jobs create pubsub ai-news-daily \
    --schedule="0 8 * * 1-5" \
    --time-zone="America/Denver" \
    --topic=ai-news-trigger \
    --message-body='{"trigger":"scheduled"}' \
    --location=us-central1 \
    --project="$PROJECT_ID" \
    --description="AI News Digest - Weekdays at 8 AM MST"

echo "✅ Schedule updated!"
echo ""
echo "New schedule: Monday-Friday at 8:00 AM Mountain Time"
echo "Weekend episodes will be included in Monday's digest"