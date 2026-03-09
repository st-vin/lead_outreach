## Lead Outreach Tool v2

Lead Outreach Tool v2 is a small, focused web application for turning raw business lead data (for example, CSV exports of local businesses) into structured, ready-to-send outreach messages. It provides a guided upload flow, automatic column detection and validation, opportunity scoring, optional AI-assisted pitch generation, and basic status tracking so you can move from leads in a spreadsheet to conversations in a messaging app in a few minutes.

### Vision

- **Practical first**: Make it easy for a solo operator or small team to run high-quality outreach campaigns without needing a complex CRM or heavy marketing stack.
- **Data in, pitches out**: Start from a CSV, clean and validate the data, generate tailored outreach messages, and keep track of what has been contacted, skipped, or needs follow-up.
- **Resilient by design**: Handle unreliable networks, flaky APIs, and concurrent users gracefully through timeouts, retry logic, safe database configuration, and clear user feedback.
- **Extensible foundation**: Provide a clean architecture (routes, services, utilities) that can be extended to new channels, models, and data sources without rewriting the core.

### What the Application Provides

- **CSV-based lead intake** with a 3-step upload and confirmation flow.
- **Automatic column detection** with confidence scores and human confirmation before import.
- **Data cleaning and validation**, including phone normalization and skip reporting.
- **Campaign and business management** with simple dashboards and detail views.
- **Pitch generation service** that can use:
  - A template-based fallback (no external API required).
  - Optional Cerebras API integration for AI-generated pitches when an API key is configured.
- **Real-time batch progress** via Server-Sent Events (SSE) during pitch generation.
- **Secure storage** of sensitive settings with an encryption key persisted on disk.

For a more detailed, step-by-step tour of current features and architecture, see `QUICKSTART.md`.

---

### Requirements

- **Python**: 3.10 or later (3.12 recommended).
- **Operating systems**: Windows, macOS, or any recent Linux distribution.
- **Package manager**:
  - Either **uv** (recommended for fast, reproducible installs), or
  - Standard **pip** with virtual environments.

---

### Quick Setup with `uv` (Recommended)

#### 1. Install `uv`

- **macOS / Linux**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- **Windows (PowerShell)**:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Restart your shell so that `uv` is on your `PATH`, then confirm:

```bash
uv --version
```

#### 2. Create an isolated environment and install dependencies

From the project root (`lead-outreach-tool-v2`):

```bash
uv venv .venv
uv pip install -r requirements.txt
```

Activate the environment:

- **macOS / Linux**:

```bash
source .venv/bin/activate
```

- **Windows (PowerShell or Command Prompt)**:

```powershell
.venv\Scripts\activate
```

#### 3. Run the application with `uv`

With the virtual environment active:

```bash
uv run python main.py
```

The application will start on `http://localhost:5000` by default.

---

### Quick Setup with `pip` (All Operating Systems)

If you prefer to use the standard Python toolchain:

#### 1. Create and activate a virtual environment

From the project root:

```bash
python -m venv .venv
```

Activate the environment:

- **macOS / Linux**:

```bash
source .venv/bin/activate
```

- **Windows (PowerShell or Command Prompt)**:

```powershell
.venv\Scripts\activate
```

#### 2. Install dependencies

With the environment active:

```bash
pip install -r requirements.txt
```

#### 3. Run the application

```bash
python main.py
```

The application will start on `http://localhost:5000`.

---

### First-Time Use Flow

Once the server is running and you have opened `http://localhost:5000` in your browser:

1. **Configure basic settings** (optional but recommended) using the Settings page. If you intend to use AI-generated pitches, add your Cerebras API key here.
2. **Upload a CSV file** of leads using the 3-step upload flow:
   - Upload the file.
   - Review detected column mappings and confidence scores.
   - Confirm the import and review any skipped rows with reasons.
3. **Create or open a campaign** to:
   - Generate pitches in batches with real-time progress,
   - Inspect and edit individual pitches,
   - Track whether a lead has been contacted or requires follow-up.

For quick manual verification and additional testing commands, refer to the checklists in `QUICKSTART.md`.

---

### Project Direction

This repository is intended as a pragmatic, production-ready starting point for small-scale lead outreach operations. The focus is on:

- Keeping the core experience as simple as possible for non-technical users.
- Providing clear internal boundaries between routing, business logic, and infrastructure.
- Making it straightforward to:
  - Swap out the model provider,
  - Integrate with additional messaging channels,
  - Migrate from SQLite to a hosted database, or
  - Extend the data model to support more advanced campaign workflows.

If you build on top of this project, aim to preserve these properties: clear flows, predictable behavior under failure, and a small, understandable surface area.

