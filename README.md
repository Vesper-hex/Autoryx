# Autoryx — Personal STEP Assignment Automation Agent

> **Your Assignment. Automated.**

Autoryx is an intelligent, private, single-user assignment automation system designed specifically for the STEP Semester 3 coursework workflow.

It automates receiving programming assignments, extracting individual questions, generating source code in **C++, C, Java, or Python**, compiling in an isolated sandbox, executing sample test cases, applying bounded automated repairs, strictly isolating generated output under `STEP_Agent_Assignments/`, and publishing to dedicated GitHub branches on [`Highorder-Thinking/Step_semester_3`](https://github.com/Highorder-Thinking/Step_semester_3).

---

## 🌟 Key Features

1. **Intelligent Intake & Question Extraction**
   - Drag-and-drop support for text-based and scanned PDFs, screenshots, and plain text.
   - Deterministic and structured question extraction isolating title, constraints, and sample I/O pairs.
   - Interactive review screen permitting inline edits to question statements, filenames, and test cases before generation.

2. **Modular Multi-Language AI Generation**
   - Pluggable provider architecture supporting **Google Gemini** (`gemini-2.5-flash`), **OpenAI** (`gpt-4o`), and a high-fidelity **Deterministic Offline Provider** for zero-cost testing.
   - Automatic removal of Markdown fences, greetings, and conversational filler.
   - Generates clean, standalone source files matching target naming standards (e.g., `question_01.cpp`, `Q1.java`).

3. **Isolated Sandbox Compilation & Bounded Repair**
   - Native compiler support for **C++ (g++ 14.2)**, **C (gcc 14.2)**, **Java (javac/java 25)**, and **Python (3.13)**.
   - Sandboxed execution with sanitized environment variables, memory limits, and strict process execution timeouts.
   - Automated repair loop sending compilation errors and test failure diffs back to the AI model (bounded to a configurable limit, default 2 attempts).
   - Preserves complete repair history and per-test execution breakdowns.

4. **Strict Repository Isolation & Safety Gatekeeper**
   - **100% Folder Isolation**: All generated output is placed strictly under `STEP_Agent_Assignments/`.
   - **Protected Existing Coursework**: Existing folders (`Week 1/`, `Week 2/`, etc.) and root repo files are strictly protected and treated as read-only.
   - Path traversal (`..`), absolute paths, unsafe symbolic links, and shell metacharacters are strictly rejected.
   - Never uses `git add .` or `git add -A`. Stages only explicitly validated output files.
   - Never force-pushes (`--force`) and never automatically merges into `main`.
   - Publishes through dedicated branches: `autoryx/assignment-<job-id>`.
   - Secret scanner ensures tokens or API keys are never published.

5. **Cloud-Ready Background Processing**
   - Persistent background queue with SQLite/PostgreSQL state storage.
   - Jobs continue processing in the background even if the laptop is closed or the browser tab is refreshed.
   - Automatic stale job recovery on system startup.

6. **Premium Developer Interface**
   - Near-black palette (`#07090e`, `#0b0f17`), subtle borders (`#1f2738`), restrained violet & cyan accents.
   - Multi-panel coding workspace (Questions list, Code editor, Validation console, GitHub Publishing drawer).
   - Real-time GitHub repository explorer reflecting the remote folder tree and branch structure.

---

## 📂 Project Directory Structure

```
Autoryx/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint & SPA mounting
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic settings & environment configuration
│   │   │   ├── database.py             # SQLAlchemy session & SQLite/Postgres engine
│   │   │   ├── logging.py              # Structured, secret-sanitizing logging
│   │   │   └── security.py             # Security utilities
│   │   ├── models/                     # SQLAlchemy models
│   │   │   ├── assignment.py           # Assignment & Question entities
│   │   │   ├── job.py                  # Job & GeneratedSolution entities
│   │   │   └── activity.py             # ActivityLog & Setting entities
│   │   ├── schemas/                    # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── ingestion/              # PDF and document text extraction
│   │   │   ├── extraction/             # Question parser & metadata extractor
│   │   │   ├── generation/             # Gemini, OpenAI, and Mock code generators
│   │   │   ├── validation/             # Isolated sandbox, C++/C/Java/Python compilers
│   │   │   │   ├── sandbox_runner.py   # Subprocess runner with timeout & env stripping
│   │   │   │   ├── repair_service.py   # Bounded retry repair loop
│   │   │   │   └── compilers/          # g++, gcc, javac, and python runners
│   │   │   ├── organization/           # STEP_Agent_Assignments structure builder
│   │   │   └── github/
│   │   │       ├── repo_safety.py      # Strict safety gatekeeper
│   │   │       ├── github_client.py    # GitHub REST API client
│   │   │       └── publishing_service.py # Atomic Git Data API branch publisher
│   │   ├── workers/
│   │   │   ├── job_queue.py            # Persistent background worker queue
│   │   │   └── tasks.py                # Asynchronous state-machine job runner
│   │   └── api/                        # REST API routers (/api/health, /api/jobs, etc.)
│   ├── tests/                          # Automated pytest suite (18 tests)
│   ├── requirements.txt                # Python dependencies
│   ├── run.py                          # Server launcher
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/layout/          # Sidebar, TopNav, and Shell
│   │   ├── features/
│   │   │   ├── dashboard/              # Overview dashboard
│   │   │   ├── new-assignment/         # Document intake & review
│   │   │   ├── workspace/              # Multi-panel coding & validation interface
│   │   │   ├── history/                # Searchable job history
│   │   │   ├── repository/             # GitHub file explorer
│   │   │   ├── activity/               # Live activity audit logs
│   │   │   └── settings/               # System configuration & key management
│   │   ├── lib/                        # API client and TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── scripts/
│   ├── start_backend.ps1               # PowerShell backend launcher
│   ├── start_frontend.ps1              # PowerShell frontend dev server
│   └── run_tests.ps1                   # Full test suite runner
├── docker-compose.yml                  # Production Compose setup
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.worker
├── .env.example
└── README.md
```

---

## ⚡ Quickstart (Windows PowerShell)

### Prerequisites
- Python 3.12+ (Python 3.13 is verified)
- Node.js 20+ & npm (Node v24 is verified)
- MinGW-W64 GCC/G++ (`g++ --version`)
- Java JDK (`javac -version`)
- Git (`git --version`)

### 1. Launch Backend Server
In PowerShell:
```powershell
cd c:\Users\divya\OneDrive\Desktop\Autoryx\backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python run.py
```
> The backend will start on **`http://127.0.0.1:8000`** with the persistent background worker listening for jobs.

### 2. Launch Frontend (Development Mode)
In a separate PowerShell window:
```powershell
cd c:\Users\divya\OneDrive\Desktop\Autoryx\frontend
npm install
npm run dev
```
> Open **`http://localhost:5173`** in your browser. All `/api` requests are automatically proxied to the backend.
> *(Alternatively, open `http://127.0.0.1:8000` directly to view the production build served by FastAPI).*

---

## 🧪 Automated Test Suite

Run the full automated test suite anytime using:
```powershell
cd c:\Users\divya\OneDrive\Desktop\Autoryx
.\scripts\run_tests.ps1
```

Or run pytest directly:
```powershell
cd c:\Users\divya\OneDrive\Desktop\Autoryx\backend
.\venv\Scripts\pytest -v
```

### Verified Test Results (18/18 Passed)
- `tests/test_health.py::test_health_check_endpoint` — PASSED
- `tests/test_document_ingestion.py::test_validate_upload_limits` — PASSED
- `tests/test_document_ingestion.py::test_extract_questions_rule_based` — PASSED
- `tests/test_repo_safety.py::test_validate_allowed_staging_path` — PASSED
- `tests/test_repo_safety.py::test_reject_paths_outside_isolated_directory` — PASSED
- `tests/test_repo_safety.py::test_reject_path_traversal` — PASSED
- `tests/test_repo_safety.py::test_reject_absolute_paths` — PASSED
- `tests/test_repo_safety.py::test_reject_malicious_and_reserved_filenames` — PASSED
- `tests/test_repo_safety.py::test_branch_name_safety` — PASSED
- `tests/test_repo_safety.py::test_content_safety_check_detects_tokens` — PASSED
- `tests/test_sandbox_validation.py::test_cpp_compilation_and_test_pass` — PASSED
- `tests/test_sandbox_validation.py::test_cpp_compilation_failure_handling` — PASSED
- `tests/test_sandbox_validation.py::test_python_runner_pass` — PASSED
- `tests/test_sandbox_validation.py::test_java_compilation_and_run` — PASSED
- `tests/test_repair_service.py::test_repair_service_zero_repairs_when_passing` — PASSED
- `tests/test_repair_service.py::test_repair_service_bounded_attempts` — PASSED
- `tests/test_git_publishing_isolated.py::test_isolated_git_staging_and_branch_in_temp_repo` — PASSED
- `tests/test_end_to_end_job.py::test_end_to_end_assignment_job_pipeline` — PASSED

---

## 🔒 How to Connect GitHub Securely

1. Navigate to **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**.
2. Generate a token scoped **only** to the repository `Highorder-Thinking/Step_semester_3`.
3. Under **Repository Permissions**, grant:
   - **Contents**: `Read and write`
   - **Metadata**: `Read-only`
4. Open the Autoryx **Settings** tab in your browser (`http://localhost:5173`).
5. Paste your token into the **Personal Access Token (PAT)** field and click **Save Configuration**.
6. Click **Test Connection** to verify remote communication with `Highorder-Thinking/Step_semester_3`.

> **Security Guarantee**:
> - Tokens are stored securely on the backend database and masked (`ghp_...XXXX`) in all API responses.
> - The frontend never receives raw token values.
> - Sandbox code executions are stripped of all tokens and environment secrets.

---

## 🚀 Running an End-to-End Assignment

1. Click **New Assignment** on the dashboard.
2. Enter assignment metadata:
   - **Title**: `Week 3 Practice`
   - **Week/Module**: `Week 3`
   - **Target Language**: `C++`, `Java`, `Python`, or `C`
3. Drag-and-drop your assignment PDF or paste the questions into the text tab.
4. Click **Extract Questions**.
5. Review the extracted problem statements, suggested filenames (e.g. `question_01.cpp`), constraints, and sample inputs/outputs.
6. Click **Approve & Start Automation**.
7. Autoryx automatically executes the pipeline in the background:
   `Generating → Compiling in Sandbox → Executing Sample Tests → AI Repairing (if needed) → Organizing Output under STEP_Agent_Assignments/`.
8. Once complete, inspect compiler logs, per-test results, and repair history.
9. Click **Publish to GitHub**, review the proposed file tree, and click **Confirm & Push**.
10. Autoryx creates the dedicated branch (e.g., `autoryx/assignment-<job-id>`), commits the verified files, and returns the confirmed commit SHA and link.

---

## 🐳 Cloud Deployment (Docker)

To deploy Autoryx in the cloud so background jobs continue when your laptop is turned off:

```bash
docker compose up -d --build
```

This starts:
- `db`: PostgreSQL 16 container for persistent job history.
- `redis`: Redis 7 container for worker coordination.
- `backend`: FastAPI API service.
- `worker`: Continuous background worker running compilers and AI pipeline.
- `frontend`: Production Nginx web server on port 5173.
