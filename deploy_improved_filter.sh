#!/bin/bash
# Deploy improved AI content filter to Google Cloud Functions

PROJECT_ID="slack-ai-news-feed"
FUNCTION_NAME="ai-news-summarizer"
REGION="us-central1"

echo "🚀 Deploying improved AI content filter..."
echo ""
echo "📋 Changes included:"
echo "  ✅ Multi-stage AI content filtering"
echo "  ✅ Better exclusion patterns for non-AI content"
echo "  ✅ Fixed false positives (Nintendo, walking pads, legal news)"
echo "  ✅ Improved keyword matching logic"
echo "  ✅ Code linting fixes"
echo ""

# Deploy the function (preserves existing trigger and schedule)
echo "📦 Deploying to Google Cloud Functions..."

gcloud functions deploy ${FUNCTION_NAME} \
    --source=. \
    --trigger-topic=ai-news-trigger \
    --runtime=python311 \
    --entry-point=main_function_digest \
    --memory=512MB \
    --timeout=540s \
    --region=${REGION} \
    --set-env-vars="ENVIRONMENT=production,FIRESTORE_COLLECTION=processed_items" \
    --project="${PROJECT_ID}" \
    --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🎯 The improved filter will now exclude:"
    echo "  • Gaming news (Nintendo, consoles)"
    echo "  • Hardware reviews (unless AI-specific)"
    echo "  • Legal/privacy news (unless AI-focused)"
    echo "  • General tech infrastructure"
    echo "  • Social media updates"
    echo ""
    echo "📊 Next steps:"
    echo "  1. The 8am trigger remains unchanged"
    echo "  2. Test manually: gcloud pubsub topics publish ai-news-trigger --message='{}'"
    echo "  3. View logs: gcloud functions logs read ${FUNCTION_NAME} --limit=50"
    echo ""
    echo "⚠️  IMPORTANT: Remember to rotate the API keys that were exposed!"
else
    echo ""
    echo "❌ Deployment failed"
    echo "Please check the error messages above"
fi