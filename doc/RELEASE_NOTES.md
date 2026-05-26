# Release v1.0.0

## 🎉 Initial Release - Pre-built Client Included

This release includes a pre-built client application so you can clone and run immediately without needing to build the frontend yourself.

## 📦 Quick Start

### Super Simple Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/databricks-solutions/project-0xfffff.git
   cd project-0xfffff
   ```

2. **Download the pre-built client:**
   - Go to the [Releases page](https://github.com/databricks-solutions/project-0xfffff/releases)
   - Download `client-build.tar.gz` from the latest release
   - Extract it:
   ```bash
   tar -xzf client-build.tar.gz -C client/build/
   ```

3. **Run the server:**
   ```bash
   uv run uvicorn server.app:app --reload --port 8000
   ```

4. **Open your browser:**
   ```
   http://localhost:8000
   ```

### Build Client Yourself (For Development Only)

If you want to modify the client or rebuild from source:

```bash
cd client
npm install
npm run build
cd ..
uv run uvicorn server.app:app --reload --port 8000
```

## ✨ Features in This Release

### Core Functionality
- **Workshop Management**: Create and manage annotation workshops
- **Discovery Phase**: Users explore traces and identify patterns
- **Annotation Phase**: Rate traces based on custom rubrics
- **IRR Analysis**: Calculate inter-rater reliability metrics
- **MLflow Integration**: Import traces from MLflow experiments

### Key Fixes & Improvements

1. **Annotation Editing** - Users can edit previous ratings with smart change detection
2. **Authentication Fix** - Resolved "permission denied" errors requiring page refresh
3. **Comment Handling** - Multi-line comments with proper newline preservation
4. **Rubric Format** - Fixed question parsing with improved delimiter
5. **Trace Randomization** - Per-user randomized but consistent trace ordering
6. **MLflow Deeplink Fix** - Removed trailing slash causing deeplink hangs

## 📋 Requirements

- Python 3.10+
- uv (Python package installer)
- Modern web browser

## 🔧 Configuration

See the [Facilitator Guide](/FACILITATOR_GUIDE) and [Lakebase Setup](/lakebase-setup) for detailed configuration, including:
- Database setup
- Databricks integration
- Authentication configuration
- Workshop creation

## 📚 Documentation

- [Specs Index](/specs/) — searchable specifications index
- [Facilitator Guide](/FACILITATOR_GUIDE) — deployment and workshop facilitation
- [BUILD_AND_DEPLOY_SPEC](/specs/BUILD_AND_DEPLOY_SPEC) — build, deploy, and migrations
- [DESIGN_SYSTEM_SPEC](/specs/DESIGN_SYSTEM_SPEC) — UI theme and design tokens
- [AUTHENTICATION_SPEC](/specs/AUTHENTICATION_SPEC) — authentication and sessions
- [ANNOTATION_SPEC](/specs/ANNOTATION_SPEC) — annotation and feedback
- [DATASETS_SPEC](/specs/DATASETS_SPEC) — trace datasets and randomization
- [RUBRIC_SPEC](/specs/RUBRIC_SPEC) — rubric format and parsing

## 🐛 Known Issues

None at this time. Please report issues on GitHub.

## 📝 License

See [LICENSE.md](https://github.com/databricks-solutions/project-0xfffff/blob/main/LICENSE.md) for details.

