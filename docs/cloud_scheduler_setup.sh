# Google Cloud Scheduler Jobs
# Deploy with: gcloud scheduler jobs create http <name> ...

# ─── Screener Run (7:15 PM SGT = 11:15 UTC) ───────────────────────────────────
# gcloud scheduler jobs create http sdas-screener-run \
#   --location=asia-southeast1 \
#   --schedule="15 11 * * 1-5" \
#   --uri="https://YOUR_CLOUD_RUN_URL/api/v1/scheduler/trigger" \
#   --message-body='{}' \
#   --headers="Content-Type=application/json,X-Scheduler-Secret=YOUR_SECRET" \
#   --time-zone="UTC" \
#   --attempt-deadline=300s

# To deploy this as a gcloud CLI script:
CLOUD_RUN_URL="https://sdas-backend-XXXXXXXX-as.a.run.app"
SCHEDULER_SECRET="your-scheduler-secret-here"
REGION="asia-southeast1"

create_screener_job() {
  gcloud scheduler jobs create http sdas-screener-run \
    --location=$REGION \
    --schedule="15 11 * * 1-5" \
    --uri="$CLOUD_RUN_URL/api/v1/scheduler/trigger" \
    --message-body='{}' \
    --headers="Content-Type=application/json,X-Scheduler-Secret=$SCHEDULER_SECRET" \
    --time-zone="UTC" \
    --attempt-deadline=300s \
    --description="SDAS daily screener — weekdays 7:15 PM SGT"
}

echo "Run create_screener_job() to create the scheduler job."
echo "Update CLOUD_RUN_URL and SCHEDULER_SECRET first!"
