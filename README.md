# JIRA Agent
## Setup and Installation

### Prerequisites 

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation) (to manage dependencies)
- Git (for cloning the repository, see [Installation Instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
<!-- - Google Cloud CLI ([Installation Instructions](https://cloud.google.com/sdk/docs/install)) -->

### Installation

1. Clone the repository:

```bash
git clone https://github.com/sally-chen-appier/jira-agent.git
cd jira-agent
```

2. Configure environment variables (via `.env` file):

#### Gemini API Authentication

There are two different ways to authenticate with Gemini models:

- Calling the Gemini API directly using an API key created via Google AI Studio.
- Calling Gemini models through Vertex AI APIs on Google Cloud.

> TIP: 
> If you just want to run the sample locally, an API key from Google AI Studio is the quickest way to get started.
> 
> If you plan on deploying to Cloud Run, you may want to use Vertex AI.

<details open>
<summary>Gemini API Key</summary> 

Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

Create a `.env` file by running the following (replace `<your_api_key_here>` with your API key, and `<your_jira_token>` with your Jira API token):

```sh
echo "GOOGLE_API_KEY=<your_api_key_here>" >> .env \
&& echo "GOOGLE_GENAI_USE_VERTEXAI=FALSE" >> .env \
&& echo "JIRA_TOKEN=<your_jira_token>" >> .env \
&& echo "JIRA_URL=https://appier.atlassian.net/" >> .env
```

</details>

<details>
<summary>Vertex AI</summary>

To use Vertex AI, you will need to [create a Google Cloud project](https://developers.google.com/workspace/guides/create-project) and [enable Vertex AI](https://cloud.google.com/vertex-ai/docs/start/cloud-environment).

Authenticate and enable Vertex AI API:

```bash
gcloud auth login
# Replace <your_project_id> with your project ID
gcloud config set project <your_project_id>
gcloud services enable aiplatform.googleapis.com
```

Create a `.env` file by running the following (replace `<your_project_id>` with your project ID, and `<your_jira_token>` with your Jira API token):

```sh
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> .env \
&& echo "GOOGLE_CLOUD_PROJECT=<your_project_id>" >> .env \
&& echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env \
&& echo "JIRA_TOKEN=<your_jira_token>" >> .env \
&& echo "JIRA_URL=https://appier.atlassian.net/" >> .env
```

</details>


There is an example `.env` file located at [.env.example](.env.example) if you would like to
verify your `.env` was set up correctly.

### Virtual Environment
1. Create virtual environment
  ```bash
  uv venv
  ```
2. Install packages
  ```bash
  uv sync
  ```

## Run the services locally
1. Iniciate virtual environment
    ```bash
    source .venv/bin/activate
    ```
1. Through the CLI (`adk run`):

    ```bash
    adk run agent
    ```
1. Through the web interface (`adk web`):

    ```bash
    adk web
    ```

The command `adk` web will start a web server on your machine and print the URL.

## Deployment

### Deploy with Docker

1. Build the Docker image:

```bash
docker build -t jira-agent .
```

2. Run the container:

```bash
docker run -p 8080:8080 --env-file .env jira-agent
```

The agent will be available at `http://localhost:8080`.

### Deploy to Google Cloud Run

#### Quick Deploy (Using Script)

The easiest way to deploy is using the provided deployment script:

```bash
./deploy.sh <your_project_id> [region]
```

The script will:
- Enable required APIs
- Create secrets for Jira token (if they don't exist)
- Grant necessary permissions
- Deploy the service to Cloud Run

#### Manual Deploy

1. **Prerequisites:**
   - Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
   - Authenticate: `gcloud auth login`
   - Set your project: `gcloud config set project <your_project_id>`
   - Enable required APIs:
     ```bash
     gcloud services enable run.googleapis.com
     gcloud services enable cloudbuild.googleapis.com
     gcloud services enable aiplatform.googleapis.com
     ```

2. **Build and deploy:**

   Using gcloud CLI:
   ```bash
   gcloud run deploy jira-agent \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=<your_project_id>,GOOGLE_CLOUD_LOCATION=us-central1,JIRA_URL=https://appier.atlassian.net/" \
     --set-secrets "JIRA_TOKEN=jira-token:latest"
   ```

   Or using Docker:
   ```bash
   # Build the image
   docker build -t gcr.io/<your_project_id>/jira-agent .
   
   # Push to Google Container Registry
   docker push gcr.io/<your_project_id>/jira-agent
   
   # Deploy to Cloud Run
   gcloud run deploy jira-agent \
     --image gcr.io/<your_project_id>/jira-agent \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=<your_project_id>,GOOGLE_CLOUD_LOCATION=us-central1,JIRA_URL=https://appier.atlassian.net/" \
     --set-secrets "JIRA_TOKEN=jira-token:latest"
   ```

3. **Configure secrets (if needed):**
   ```bash
   # Create a secret for Jira token
   echo -n "<your_jira_token>" | gcloud secrets create jira-token --data-file=-
   ```

4. **Access your deployed agent:**
   After deployment, Cloud Run will provide you with a URL like:
   `https://jira-agent-xxxxx-uc.a.run.app`

### Environment Variables for Deployment

When deploying, ensure the following environment variables are set:

- **For Vertex AI (recommended for Cloud Run):**
  - `GOOGLE_GENAI_USE_VERTEXAI=TRUE`
  - `GOOGLE_CLOUD_PROJECT=<your_project_id>`
  - `GOOGLE_CLOUD_LOCATION=us-central1` (or your preferred region)
  - `JIRA_TOKEN=<your_jira_token>` (optional, if using Jira tools)
  - `JIRA_URL=https://appier.atlassian.net/` (optional, defaults to Appier's Jira instance)

- **For API Key (local/Docker):**
  - `GOOGLE_API_KEY=<your_api_key>`
  - `GOOGLE_GENAI_USE_VERTEXAI=FALSE`
  - `JIRA_TOKEN=<your_jira_token>` (optional, if using Jira tools)
  - `JIRA_URL=https://appier.atlassian.net/` (optional, defaults to Appier's Jira instance)

> **Note:** For production deployments, use Google Cloud Secret Manager to store sensitive values like API keys and tokens instead of environment variables.