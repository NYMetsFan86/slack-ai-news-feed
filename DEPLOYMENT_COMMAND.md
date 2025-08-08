# Deployment Command for Improved AI Filter

Since you're already authenticated, run this command from the project root directory:

```bash
gcloud functions deploy ai-news-summarizer \
    --source=. \
    --trigger-topic=ai-news-trigger \
    --runtime=python311 \
    --entry-point=main_function_digest \
    --memory=512MB \
    --timeout=540s \
    --region=us-central1 \
    --set-env-vars="ENVIRONMENT=production,FIRESTORE_COLLECTION=processed_items" \
    --project="slack-ai-news-feed" \
    --quiet
```

## What This Does

1. **Deploys a new revision** of the Cloud Function with the improved AI filter
2. **Preserves the existing trigger** (ai-news-trigger topic)
3. **Maintains the 8am schedule** (Cloud Scheduler remains unchanged)
4. **Uses existing environment variables** from your Cloud Function

## After Deployment

1. **Test the deployment:**
   ```bash
   gcloud pubsub topics publish ai-news-trigger --message='{"test":true}'
   ```

2. **Check logs:**
   ```bash
   gcloud functions logs read ai-news-summarizer --limit=50
   ```

3. **Verify the schedule is unchanged:**
   ```bash
   gcloud scheduler jobs list --location=us-central1
   ```

## Important Notes

- The 8am trigger will NOT be disrupted
- The Cloud Scheduler job remains unchanged
- Only the function code is updated
- Environment variables need to be set in the Cloud Function (not from local .env files)

## Don't Forget

⚠️ **ROTATE YOUR API KEYS** - The exposed credentials in env-vars.yaml need to be replaced ASAP!