#!/bin/bash

# Deployment script for JIRA Agent to Google Cloud Run
# Usage: ./deploy.sh [project_id] [region]

set -e

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT}}
REGION=${2:-us-central1}
SERVICE_NAME="jira-agent"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID is required"
    echo "Usage: ./deploy.sh <project_id> [region]"
    echo "Or set GOOGLE_CLOUD_PROJECT environment variable"
    exit 1
fi

echo "Deploying $SERVICE_NAME to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check if secrets exist, create if they don't
echo ""
echo "Checking secrets..."

if ! gcloud secrets describe jira-token --project="$PROJECT_ID" &> /dev/null; then
    echo "Creating jira-token secret..."
    read -sp "Enter Jira API Token: " JIRA_TOKEN
    echo ""
    echo -n "$JIRA_TOKEN" | gcloud secrets create jira-token --data-file=- --project="$PROJECT_ID"
else
    echo "jira-token secret already exists"
fi

# Grant Cloud Run service account access to secrets
echo ""
echo "Granting Cloud Run service account access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding jira-token \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" || true

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},JIRA_URL=https://appier.atlassian.net/" \
    --set-secrets "JIRA_TOKEN=jira-token:latest" \
    --project="$PROJECT_ID"

echo ""
echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" --project="$PROJECT_ID"

