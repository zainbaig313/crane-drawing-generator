# AI Usage Log (`AI_LOG.md`)

**Project:** Parametric Overhead Crane Drawing Generator

---

## 1. AI Tools Used and What For

- **ChatGPT (GPT):** Used during the initial planning and problem-framing phase. I used it to break down the assignment requirements, analyze the sample crane drawing image, decide on the crane type and projection view, figure out the required user inputs, and draft a detailed implementation prompt.
- **Google Antigravity IDE (Gemini 3.8 Flash - High):** Used for the actual development, workspace setup, Django backend/frontend code generation, SVG drawing logic, and documentation. *(Note: I normally prefer Claude for code-heavy tasks, but since I was working with free/limited model access, I used Gemini for this build.)*

---

## 2. Key Prompts Used

### Prompt 1 — Discovering Required Inputs from the Sample Drawing (ChatGPT)
> *(Provided the sample assignment image)*
> "Let me ask you one thing: what input data from the user/engineer would I need to generate the exact drawing for those inputs? For example, if I build a website where a user enters inputs and after submitting them the website generates the exact same 2D drawing, what parameters will the user input?"

- **Purpose:** Identified the 8 core parameters (capacity, span, lifting height, girder depth, end carriage height, trolley width, hook block height, and runway rail height) needed to drive a parametric drawing.

### Prompt 2 — Checking Scope & Crane Type Freedom (ChatGPT)
> "Did they give me a free hand that I can select any crane type? Which view to draw?"

- **Purpose:** Confirmed that keeping the scope focused on a single crane type and a single 2D view was appropriate for a V1 prototype instead of overcomplicating the project.

### Prompt 3 — Selecting the View & Finalizing Parameter Count (ChatGPT)
> "Which view would be easy to draw? Front elevation — how many parameters would I need from a user to generate the following view?"

- **Purpose:** Locked in the **Single-Girder Overhead Travelling Crane (Front Elevation)** scope and finalized the exact parameter list.

### Prompt 4 — Generating the Master Specification Prompt (ChatGPT)
> "Write a detailed prompt for my Antigravity IDE so I can give it and it starts building the project with all the user requirements and validation."

- **Purpose:** Turned our requirement breakdown into a structured engineering specification covering architecture, validation rules, SQLite models, DRF API endpoints, Bootstrap 5 UI pages, and a mandatory "plan-first, wait for approval" workflow.

### Prompt 5 — Building the Application (Antigravity IDE / Gemini 3.8 Flash)
> *(Passed the full ChatGPT-generated specification prompt: `# Project: Parametric Overhead Crane Drawing Generator`)*
> Included the full stack constraints (Django, DRF, SQLite, Bootstrap 5, Vanilla JS, Python-generated SVG), the 8 parameters with validation bounds, API endpoints, and the instruction: *"For now, DO NOT BUILD ANYTHING. Inspect the workspace, understand the existing project state, and present your proposed implementation plan. Wait for my explicit approval before writing code or making any changes."*

- **Purpose:** Guided the IDE agent to inspect the empty workspace, propose a clean architecture first, and build the project step by step after approval.

---

## 3. Where the AI Was Wrong & How I Caught It

Because of time constraints, I did not audit every line of the backend code in detail, but I caught clear issues by running and visually testing the application in the browser:

1. **Redundant UI Buttons & Exposed REST API Link in the Navbar:**
   - **What the AI did wrong:** The AI added three separate "Create" buttons visible from the dashboard (two in the top navigation bar — *"Create Design"* and *"New Drawing"* — plus *"Create New Design"* on the dashboard itself) and also placed a *"REST API"* link in the navbar that took users directly to Django REST Framework's browsable API page.
   - **How I caught and fixed it:** While checking the dashboard in the browser, I immediately noticed the cluttered navbar and clicked the REST API link to see where it went. I then prompted the AI to remove the REST API button and the extra navbar create buttons, keeping only a single Create button on the dashboard.

2. **SVG Layout Issues at Minimum Input Values:**
   - **What the AI did wrong:** When testing the SVG generator with minimum allowed parameter values, the generated drawing appears cramped and messy because the fixed label/dimension offsets do not adapt cleanly at the smallest scale.
   - **How I caught it:** Spotted during manual testing with minimum boundary inputs. With more time and a targeted follow-up prompt, the label spacing and dimension offsets can be tuned to handle minimum-scale drawings cleanly.
