#!/bin/bash
# Production deployment script for AI News Summarizer

set -e

echo "🚀 AI News Summarizer - Production Deployment"
echo "============================================"

# Add gcloud to PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Check gcloud installation
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found in PATH"
    echo "   Try: export PATH=\"\$HOME/google-cloud-sdk/bin:\$PATH\""
    exit 1
fi

echo "✅ Found gcloud: $(which gcloud)"

# Check authentication
echo ""
echo "🔐 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud"
    echo "   Running: gcloud auth login"
    gcloud auth login
else
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    echo "✅ Authenticated as: $ACTIVE_ACCOUNT"
fi

# Check project
echo ""
echo "🏗️ Checking project configuration..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No project set"
    echo "   Available projects:"
    gcloud projects list --format="table(projectId,name)"
    echo ""
    read -p "Enter your project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    echo "✅ Current project: $CURRENT_PROJECT"
    read -p "Is this correct? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        read -p "Enter correct project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
fi

# Update project variable
PROJECT_ID=$(gcloud config get-value project)

# Check for required environment variables
echo ""
echo "🔧 Checking environment variables..."

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   Please edit .env with your values"
    exit 1
fi

# Source .env file (use GCP version if exists)
if [ -f .env.gcp ]; then
    echo "Using .env.gcp for deployment"
    set -a
    source .env.gcp
    set +a
else
    set -a
    source .env
    set +a
fi

# Validate required variables
MISSING_VARS=()
[ -z "$OPENROUTER_API_KEY" ] && MISSING_VARS+=("OPENROUTER_API_KEY")
[ -z "$SLACK_WEBHOOK_URL" ] && MISSING_VARS+=("SLACK_WEBHOOK_URL")

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '   - %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Please add these to your .env file"
    exit 1
fi

echo "✅ All required environment variables found"

# Check Firestore
echo ""
echo "🗄️ Checking Firestore..."
if gcloud firestore databases describe --database="(default)" &>/dev/null; then
    echo "✅ Firestore (default) database exists"
else
    echo "❌ Firestore not initialized"
    echo "   Creating Firestore database..."
    gcloud firestore databases create --location=us-central1 --database="(default)"
fi

# Enable required APIs
echo ""
echo "🔌 Enabling required APIs..."
APIS=(
    "cloudfunctions.googleapis.com"
    "firestore.googleapis.com"
    "cloudscheduler.googleapis.com"
    "pubsub.googleapis.com"
    "cloudbuild.googleapis.com"
    "appengine.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "   Enabling $api..."
    gcloud services enable "$api" --quiet
done

echo "✅ All APIs enabled"

# Create production .env.yaml for Cloud Functions
echo ""
echo "📝 Creating production environment configuration..."
cat > .env.yaml << EOF
OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}"
SLACK_WEBHOOK_URL: "${SLACK_WEBHOOK_URL}"
GOOGLE_CLOUD_PROJECT: "${PROJECT_ID}"
FIRESTORE_COLLECTION: "processed_items"
ENVIRONMENT: "production"
EOF

echo "✅ Created .env.yaml"

# Choose deployment method
echo ""
echo "🎯 Choose deployment method:"
echo "1. Event-driven (recommended) - Triggers on new content"
echo "2. Simple daily schedule - Runs once at 7 AM"
echo "3. Both (event-driven + backup schedule)"

read -p "Enter choice (1-3): " DEPLOY_CHOICE

case $DEPLOY_CHOICE in
    1)
        echo "Deploying event-driven functions..."
        ./deployment/event_driven_deploy.sh
        ;;
    2)
        echo "Deploying simple scheduled function..."
        gcloud functions deploy ai-news-summarizer \
            --runtime=python311 \
            --trigger-topic=ai-news-trigger \
            --entry-point=main_function_digest \
            --source=. \
            --memory=512MB \
            --timeout=540s \
            --env-vars-file=.env.yaml \
            --region=us-central1 \
            --project="${PROJECT_ID}"
        
        # Create scheduler
        gcloud scheduler jobs create pubsub ai-news-daily \
            --schedule="0 7 * * *" \
            --time-zone="America/Denver" \
            --topic=ai-news-trigger \
            --message-body='{"trigger":"scheduled"}' \
            --location=us-central1 \
            --project="${PROJECT_ID}"
        ;;
    3)
        echo "Deploying both event-driven and scheduled..."
        ./deployment/event_driven_deploy.sh
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Clean up sensitive files
echo ""
echo "🧹 Cleaning up..."
rm -f .env.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Next steps:"
echo "1. Monitor function logs:"
echo "   gcloud functions logs read --limit=50"
echo ""
echo "2. Test manually:"
echo "   gcloud pubsub topics publish ai-news-trigger --message='test'"
echo ""
echo "3. View in Cloud Console:"
echo "   https://console.cloud.google.com/functions/list?project=${PROJECT_ID}"