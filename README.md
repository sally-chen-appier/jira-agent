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

Create a `.env` file by running the following (replace `<your_api_key_here>` with your API key and `<your_github_pat_here>` with your GitHub Personal Access Token):

```sh
echo "GOOGLE_API_KEY=<your_api_key_here>" >> .env \
&& echo "GOOGLE_GENAI_USE_VERTEXAI=FALSE" >> .env \
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

Create a `.env` file by running the following (replace `<your_project_id>` with your project ID and `<your_github_pat_here>` with your GitHub Personal Access Token):

```sh
echo "GOOGLE_GENAI_USE_VERTEXAI=TRUE" >> .env \
&& echo "GOOGLE_CLOUD_PROJECT=<your_project_id>" >> .env \
&& echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env \
&& echo "GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_pat_here>" >> .env
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