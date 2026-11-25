# Parametric Overhead Crane Drawing Generator

A web application for generating parametric 2D front-elevation drawings of single-girder overhead travelling (EOT) cranes from dimensional and capacity parameters.

Built with Python, Django, Django REST Framework, and pure-Python SVG generation.

---

## 1. Project Overview

In industrial material handling, early-stage project scoping requires rapid spatial layout validation before detailed structural finite element analysis (FEA) or manufacturing detailing begins. 

This application provides an engineering-oriented prototype that:
- Accepts 8 primary crane design parameters (capacity, span, lift height, girder depth, etc.).
- Performs strict backend validation with domain-specific software safety boundaries and cross-field spatial checks.
- Programmatically generates an exact, dimensioned 2D engineering front-elevation drawing as an SVG vector graphic.
- Persists designs in an SQLite database as reproducible parameters (never storing stale raster images).
- Exposes a headless REST API alongside a responsive Bootstrap 5 web interface with live drawing previews.

> **Disclaimer:** This tool is a parametric drawing generator for layout scoping and visualization. It is **not** a certified structural engineering calculation system and must not be used for crane fabrication, load rating certification, or structural sign-off.

---

## 2. Technology Stack & Architectural Justifications

| Component | Technology | Rationale |
|---|---|---|
| **Backend Framework** | Python 3.11 & Django 4.2 | High maintainability, robust built-in ORM, secure form handling, and native templating within a single coherent project structure. |
| **REST API** | Django REST Framework (DRF) 3.14 | Standardized serialization, strict input validation, clear HTTP status codes (`201`, `400`, `404`), and decoupling of data operations from presentation. |
| **Drawing Engine** | Pure Python SVG (`xml.etree` / formatted XML) | SVG offers infinite scalability, resolution independence, precise stroke and marker control (arrowheads, extension lines), responsive browser rendering, and zero heavy binary C-dependencies. |
| **Database** | SQLite 3 | Self-contained, zero-configuration relational database ideal for local execution, prototype persistence, and test isolation. |
| **Frontend UI** | Django Templates + Bootstrap 5 | Clean, responsive industrial aesthetic without the operational complexity or build pipeline overhead of Node.js/React. |
| **Client Interactions** | Vanilla JavaScript (ES6) | Lightweight asynchronous updates (`fetch` API) for real-time SVG previews without full-page reloads. |

---

## 3. Features

- **Parametric Form with Software Validation:** Enforces positive numeric bounds, min/max checks, and cross-field compatibility rules.
- **Dynamic 2D SVG Front Elevation:** Real-time generation of the main box girder, runway rails, end carriages, hoist/trolley assembly, and hook block.
- **Accurate Dimension Lines:** Extension lines, dimension lines with engineering arrowheads, and centered numerical labels in millimetres (`mm`).
- **Professional Title Block:** Standard engineering title block detailing Project Title, Drawing Subject, Safe Working Load (SWL), Design Reference Name, Units, and Prototype Disclaimer.
- **Design Registry & History:** Dashboard listing saved configurations with instant preview, editing, and deletion capabilities.
- **SVG Export:** Direct download of generated SVG files for use in CAD tools, vector editors, or technical documentation.
- **Dual Interface:** Full graphical interface and headless REST API operating in tandem.

---

## 4. Local Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.11.9)
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "take home assigment"
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Open in browser:**
   Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 5. REST API Documentation

The REST API is mounted under `/api/` and accepts/returns JSON (`Content-Type: application/json`).

### Endpoints

#### 1. List Designs
- **Endpoint:** `GET /api/designs/`
- **Response:** `200 OK`
- **Description:** Returns an array of saved designs with summary parameters and timestamps.

#### 2. Create Design
- **Endpoint:** `POST /api/designs/`
- **Payload:**
  ```json
  {
    "design_name": "Heavy Workshop Crane",
    "capacity": "10.0",
    "span": 25000,
    "lifting_height": 7900,
    "girder_depth": 1200,
    "end_carriage_height": 500,
    "trolley_width": 1000,
    "hook_block_height": 700,
    "runway_rail_height": 100
  }
  ```
- **Responses:**
  - `201 Created` with serialized object and database `id`.
  - `400 Bad Request` with field-specific validation error details.

#### 3. Retrieve Design
- **Endpoint:** `GET /api/designs/{id}/`
- **Response:** `200 OK` (or `404 Not Found`) containing all stored parameters.

#### 4. Update Design
- **Endpoint:** `PUT /api/designs/{id}/` (or `PATCH /api/designs/{id}/`)
- **Response:** `200 OK` with updated record, or `400 Bad Request` if parameters violate constraints.

#### 5. Generate Drawing from Stored Design
- **Endpoint:** `POST /api/designs/{id}/generate-drawing/`
- **Query Params:** `?format=svg` (optional raw `image/svg+xml` response)
- **Response (`200 OK`):**
  ```json
  {
    "design_id": 1,
    "design_name": "Heavy Workshop Crane",
    "crane_type": "single_girder_overhead",
    "capacity": "10.00",
    "span": 25000,
    "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1600 1000\">...</svg>"
  }
  ```

#### 6. Live Preview (Stateless)
- **Endpoint:** `POST /api/designs/preview/`
- **Description:** Validates raw input and generates SVG on-the-fly *without* database persistence.

---

## 6. Validation Rules

Validation is centralized in `cranes/services/validation.py` to prevent duplicate logic across views and serializers:

### Configured Software Ranges
- **Capacity:** `0.01` to `20.0` Tonnes
- **Crane Span:** `5,000` to `25,000` mm
- **Lifting Height:** `100` to `15,000` mm
- **Main Girder Depth:** `100` to `2,500` mm
- **End Carriage Height:** `100` to `1,500` mm
- **Hoist/Trolley Width:** `100` to `3,000` mm
- **Hook Block Height:** `100` to `2,000` mm
- **Runway Rail Height:** `10` to `300` mm

### Cross-Field Layout Constraints
1. **Span vs. Trolley Width:** Trolley width cannot equal or exceed span, and must maintain at least 1,000 mm of clearance from total span to account for end stops.
2. **Lifting Height vs. Hook Block:** Hook block assembly height must be strictly less than total lifting height.
3. **Girder Depth vs. End Carriage:** End carriage height cannot exceed $3\times$ girder depth to prevent impossible mechanical joint geometry.

---

## 7. Drawing Generation Engine (`cranes/services/drawing_generator.py`)

1. **Aspect Ratio Preservation:** Calculates real-world bounding envelope and computes uniform scale factor $s = \min(w_{\text{avail}} / W_{\text{mm}}, h_{\text{avail}} / H_{\text{mm}})$.
2. **Component Layering:**
   - Background canvas with subtle 40px drafting grid pattern.
   - Runway beam stubs with 45° cross-hatch.
   - Left & Right Runway Rails with wheel contact surfaces.
   - End carriage trucks with wheel circles and rail sweepers.
   - Main single-girder box profile with top/bottom flange plates and internal stiffener markings.
   - Underslung trolley frame, hoist motor enclosure, and rope drum.
   - Wire rope falls and forged hook block with safety latch.
3. **Engineering Dimensioning:**
   - Dimension lines with SVG `<marker>` arrowheads.
   - Offset extension lines avoiding component overlap.
   - Monospace numerical dimension callouts with exact unit strings.
4. **Responsive Viewport:** Uses SVG `viewBox="0 0 1600 1000"` and `preserveAspectRatio="xMidYMid meet"` for fluid rendering across all screen resolutions.

---

## 8. Known Limitations

1. **Single Elevation:** Only 2D front elevation is rendered; plan (top) view, end cross-section, and side elevations are out of scope.
2. **Single-Girder Only:** Double-girder and gantry crane configurations are not supported in V1.
3. **Simplified Hook Position:** The hoist trolley is fixed at span center ($X = L/2$) for symmetrical elevation drafting.
4. **No Structural Analysis:** Deflection limits ($L/600$ or $L/800$), wheel load calculations, motor power sizing, and seismic/wind loadings are not calculated.

---

## 9. Actual Development Time Spent

I spent around **2 to 3 hours** in total working on this project. 

To be completely honest, most of the code generation were done by AI based on my requirements and instructions and prompt.

My own time was spent on:
- Writing [`DECISIONS.md`] 
- reviewing the application what  was generated.
- Cleaning up the UI and removing things that shouldn't be there (for example, getting rid of redundant create buttons and extra links on the navbar to keep the interface clean and focused).
- Double-checking that the validation rules and SVG drawing behavior actually made sense.

how ever there a still little drawing issues.



