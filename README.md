# VibeScaler

**Collaborate with your team to define what good agent behavior looks like, then turn that judgment into an automated grader that runs at scale.**

Anyone building an AI agent eventually hits the same question: is it actually doing a good job? The people who really know are the subject matter experts, the claims adjuster, the support lead, the clinician, but they can't read thousands of responses, and an off-the-shelf grader has no idea what "good" means for your business. VibeScaler is a Databricks App that closes that gap. It walks your experts through real examples of your agent to define what quality means for your use case, then aligns an LLM judge to their judgment so it scores new responses the way they would, automatically. Engineers get an evaluator they can trust and run continuously; SMEs get their standards encoded without writing code.

## How it works

VibeScaler runs an evaluation project in four stages:

1. **Discovery.** Before writing any rubric, participants investigate real examples to surface what high and low quality actually mean for their use case. Generic measures like correctness or groundedness get defined in terms of the team's own business knowledge.
2. **Annotation.** Multiple raters label real MLflow traces against the discovered criteria. The app measures inter-rater reliability so you can see where experts agree and where the definition of quality is still fuzzy.
3. **Alignment.** VibeScaler applies optimization techniques to align the LLM judge to your team's labels, so it scores the way your experts do. You get agreement metrics between the judge and your experts, so judge quality is a number you can track instead of a vibe.
4. **Evaluate at scale.** Run the aligned judge across your traces in MLflow and keep iterating as the agent and the criteria evolve.

The judges you build are standard MLflow judges. You can run them directly with MLflow, in or out of this app.

## 📚 Documentation

For detailed documentation, see the [/doc](doc/) folder:

- **[Facilitator Guide](doc/FACILITATOR_GUIDE.md)** - A comprehensive guide for facilitators to deploy, configure, and run a project.
- **[Release Notes](doc/RELEASE_NOTES.md)** - Latest release information and quick start.
- **[Changelog](doc/CHANGELOG.md)** - Full version history.
- **[All Documentation](doc/README.md)** - Complete documentation index.

## 🚀 Quick Start (Recommended)

For production use, deploy the **latest stable release** to Databricks Apps, or install it from the Databricks Marketplace. To deploy it yourself, see [Deploying to Databricks Apps](#-deploying-to-databricks-apps) below.

To develop locally instead, jump to [Local Development](#-local-development).

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 22.16+**
- **Databricks workspace** with:
  - MLflow experiments
  - Databricks Apps
- **Strongly recommended: just**
   - [Installation](https://just.systems/man/en/packages.html)
   - It's possible to use without this, but the majority of useful scripts use just.

## 🚀 Local Development

### Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The UI will be available at `http://localhost:3000`

4. **Build for production:**
   ```bash
   npm run build
   ```

### Backend Setup

#### Option 1: Using uv (Recommended ⚡)
1. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```


2. **Run the FastAPI development server in local:**
   ```bash
   uv run uvicorn server.app:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

#### Option 2: Using pip (Traditional)

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e .
   # Or for editable install with dev dependencies:
   pip install -e ".[dev]"
   ```

3. **Run the FastAPI development server:**
   ```bash
   uvicorn server.app:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`


## 🧪 End-to-End (E2E) Tests

E2E tests are run with **Playwright** against a real local stack (FastAPI + Vite) using an **isolated SQLite database**.

```bash
# Run E2E tests headless (default)
just e2e

# Run E2E tests headed (useful for debugging)
just e2e headed

# Run E2E tests in Playwright UI mode
just e2e ui

# Debugging helpers
just e2e-servers   # start API+UI against .e2e-workshop.db
just e2e-test      # run tests (assumes servers are already running)
```

## 🚢 Deploying to Databricks Apps

### 0. Prerequisites

Ensure you have the [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/tutorial) installed and configured:

```bash
databricks --version
databricks current-user me  # Verify authentication
```

### 1. Create a Databricks App

```bash
databricks apps create vibescaler
```

### 2. Build the Frontend

```bash
cd client && npm install && npm run build && cd ..
```

This creates an optimized production build in `client/build/`

### 3. Sync Files to Workspace

```bash
DATABRICKS_USERNAME=$(databricks current-user me | jq -r .userName)
databricks sync . "/Workspace/Users/$DATABRICKS_USERNAME/vibescaler"
```

Refer to the [Databricks Apps deploy documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy?language=Databricks+CLI#deploy-the-app) for more info.

### 4. Deploy the App

```bash
databricks apps deploy vibescaler \
  --source-code-path /Workspace/Users/$DATABRICKS_USERNAME/vibescaler
```

### 5. Access Your App

Once deployed, the Databricks CLI will provide a URL to access your application.


## ⚙️ Configuration

### Authentication Configuration (`config/auth.yaml`)

Configure facilitator accounts and security settings:

```yaml
facilitators:
  - email: "facilitator@email.com"
    password: "xxxxxxxxxx"
    name: "Workshop Facilitator"
    description: "Primary workshop facilitator"

security:
  default_user_password: "changeme123"
  password_requirements:
    min_length: 8
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
  session:
    token_expiry_hours: 24
    refresh_token_expiry_days: 7
```

## 🛠 Built on MLflow

VibeScaler is an orchestration layer over open-source MLflow. It reads traces from your MLflow experiments, stores human annotations alongside them, and uses MLflow's GenAI evaluation primitives (judges and the alignment optimizer, which needs `mlflow[genai]>=3.9`) to turn expert labels into an aligned judge. Prompt optimization runs on DSPy. Because the output is a standard MLflow judge, nothing about your evals is locked into this app.

## 🤝 Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to set up your environment, run the tests, and open a pull request. Bug reports and feature requests go in [Issues](https://github.com/databricks-solutions/project-0xfffff/issues).

## 🔒 Security

For security policies and how to report a vulnerability, see [SECURITY.md](SECURITY.md).

## 📄 License

See the [LICENSE.md](LICENSE.md) file for details.
