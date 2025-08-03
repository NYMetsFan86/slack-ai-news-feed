# 🏗️ Google Cloud Platform Setup Guide - Pre-Deployment Checklist

This guide covers all manual GCP setup tasks required BEFORE deploying the AI News Summarizer.

## 📋 Prerequisites Checklist

Before starting GCP setup, ensure you have:

- [ ] Google account (Gmail or Google Workspace)
- [ ] Credit card for GCP account verification (stays in free tier)
- [ ] Computer with Python 3.9+ installed
- [ ] Basic command line knowledge

## 🔐 Step 1: Google Cloud Account Setup

### 1.1 Create GCP Account
1. Go to https://cloud.google.com/
2. Click "Get started for free"
3. Sign in with your Google account
4. Accept terms and add billing information
5. You'll receive $300 in free credits (valid for 90 days)

### 1.2 Create a New Project
```bash
# Option A: Use Cloud Console (Web UI)
# 1. Go to https://console.cloud.google.com/
# 2. Click project dropdown (top left)
# 3. Click "New Project"
# 4. Project Name: "ai-news-summarizer"
# 5. Note your Project ID (e.g., "ai-news-summarizer-123456")

# Option B: Use gcloud CLI (after installing)
gcloud projects create ai-news-summarizer-$(date +%s) \
  --name="AI News Summarizer"
```

### 1.3 Enable Required APIs
Navigate to APIs & Services → Enable APIs, then enable:
- **Cloud Functions API**
- **Cloud Firestore API**
- **Cloud Scheduler API**
- **Cloud Pub/Sub API**
- **Cloud Build API** (for deploying functions)

Or use CLI:
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.4 Install gcloud CLI
```bash
# macOS
brew install google-cloud-sdk

# Windows - Download installer from:
# https://cloud.google.com/sdk/docs/install

# Linux
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Initialize and authenticate
gcloud init
gcloud auth login
```

## 🔑 Step 2: Get Required API Keys

### 2.1 OpenRouter API Key
1. Go to https://openrouter.ai/
2. Sign up for free account
3. Navigate to Keys section
4. Create new API key
5. Save the key starting with `sk-or-v1-`
6. Verify free models are available (e.g., `meta-llama/llama-3.1-8b-instruct:free`)

### 2.2 Slack Webhook URL
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App Name: "AI News Summarizer"
4. Pick your workspace
5. Navigate to "Incoming Webhooks"
6. Toggle "Activate Incoming Webhooks" to ON
7. Click "Add New Webhook to Workspace"
8. Choose your channel
9. Copy the webhook URL: `https://hooks.slack.com/services/XXX/YYY/ZZZ`

## 🏛️ Step 3: Set Up Cloud Firestore

### 3.1 Create Firestore Database
```bash
# Create Firestore database in native mode
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native

# Or use Console:
# 1. Go to Firestore in Console
# 2. Click "Create Database"
# 3. Choose "Native Mode"
# 4. Select location: us-central1
# 5. Click "Create"
```

### 3.2 Create Initial Collection
```bash
# This will be created automatically by the app
# But you can create it manually if desired:
# In Firestore Console → Start Collection → ID: "processed_items"
```

## 📬 Step 4: Set Up Pub/Sub Topic

```bash
# Create Pub/Sub topic for scheduler
gcloud pubsub topics create ai-news-trigger

# Verify topic was created
gcloud pubsub topics list
```

## ⏰ Step 5: Prepare Cloud Scheduler

Cloud Scheduler requires App Engine to be enabled:

```bash
# Enable App Engine (required for Cloud Scheduler)
gcloud app create --region=us-central

# Note: Choose the region closest to you
# Cloud Scheduler will be created after function deployment
```

## 🚀 Step 6: Prepare Your Code

### 6.1 Clone the Repository
```bash
git clone https://github.com/yourusername/ai-slack-news.git
cd ai-slack-news
```

### 6.2 Create .env File
```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

Add your credentials:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 6.3 Install Dependencies Locally
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ✅ Step 7: Validation Checklist

### GCP Access
```bash
# Check authentication
gcloud auth list

# Check current project
gcloud config get-value project

# List enabled APIs
gcloud services list --enabled
```

### Local Setup
```bash
# Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"GCP setup test successful! 🎉"}' \
  YOUR_SLACK_WEBHOOK_URL

# Test Python environment
python --version  # Should be 3.9+

# Test local execution (optional)
python main.py
```

## 📊 Step 8: Cost Estimates & Free Tier

### GCP Free Tier (Monthly)
- **Cloud Functions**: 2M invocations, 400,000 GB-seconds, 200,000 GHz-seconds
- **Firestore**: 1GB storage, 50k reads, 20k writes, 20k deletes per day
- **Pub/Sub**: 10GB of messages
- **Cloud Scheduler**: 3 free jobs

### Estimated Usage for Daily Runs
- Function invocations: ~30/month = **$0.00**
- Firestore operations: ~3,000/month = **$0.00**
- Pub/Sub messages: < 1MB/month = **$0.00**
- Scheduler jobs: 1 job = **$0.00**
- **Total: $0.00/month** (well within free tier)

### Set Up Budget Alerts
```bash
# Create budget alert for $5
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="AI News Summarizer Budget" \
  --budget-amount=5 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## 🎯 Step 9: Deploy Your Function

### 9.1 Deploy the Cloud Function
```bash
# From project root directory
gcloud functions deploy ai-news-summarizer \
  --runtime=python311 \
  --trigger-topic=ai-news-trigger \
  --entry-point=main_function \
  --memory=256MB \
  --timeout=300s \
  --env-vars-file=.env \
  --region=us-central1
```

### 9.2 Create Cloud Scheduler Job
```bash
# Create scheduler job (7 AM MST = 2 PM UTC)
gcloud scheduler jobs create pubsub ai-news-daily \
  --schedule="0 14 * * 1-5" \
  --time-zone="UTC" \
  --topic=ai-news-trigger \
  --message-body='{"trigger":"scheduled"}' \
  --location=us-central1
```

### 9.3 Test Your Deployment
```bash
# Trigger function manually
gcloud pubsub topics publish ai-news-trigger \
  --message='{"trigger":"manual"}'

# Check function logs
gcloud functions logs read ai-news-summarizer \
  --limit=50

# Test scheduler job
gcloud scheduler jobs run ai-news-daily --location=us-central1
```

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "API not enabled" | Run the enable API commands in Step 1.3 |
| "Permission denied" | Check you're using the right project: `gcloud config set project YOUR_PROJECT_ID` |
| "Quota exceeded" | Check quotas in Console → IAM & Admin → Quotas |
| "Function timeout" | Increase timeout: `--timeout=540s` (max 9 min) |
| "No Slack message" | Check function logs for errors |

### Viewing Logs
```bash
# Function logs
gcloud functions logs read ai-news-summarizer --limit=100

# Or in Console:
# Cloud Functions → ai-news-summarizer → Logs
```

## 📝 Post-Deployment Checklist

- [ ] Function deployed successfully
- [ ] Scheduler job created
- [ ] Manual test triggered
- [ ] Slack message received
- [ ] Firestore shows processed items
- [ ] Budget alerts configured
- [ ] Logs show no errors

## 🎉 Success!

Your AI News Summarizer is now running on Google Cloud Platform! It will:
- Run automatically at 7 AM MST on weekdays
- Process RSS feeds and generate summaries
- Post to your Slack channel
- Track processed items in Firestore
- Stay within free tier limits

### Next Steps
1. Monitor first automatic run
2. Adjust RSS feeds in configuration
3. Customize summarization prompts
4. Add team members to Slack channel

---

**Need Help?** 
- Check logs: `gcloud functions logs read`
- View [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review [Configuration Options](./CONFIGURATION.md)