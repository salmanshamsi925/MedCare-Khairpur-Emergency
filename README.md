# 🏥 MedCare Emergency — Khairpur Resource Manager
> **Smart Emergency Dispatch, AI-Powered Triage & Real-Time Hospital Fleet Command Console**  
> *Developed for OpenHack 2026 · Team HT-03 (Musafir Devs)*

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Leaflet](https://img.shields.io/badge/Maps-Leaflet.js-199900?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hackathon](https://img.shields.io/badge/OpenHack-2026%20Submission-red)](#)

---

## 📌 Overview

**MedCare Emergency** is a centralized healthcare emergency command platform designed for the district of **Khairpur, Sindh**. In critical medical emergencies, every second counts. MedCare automates the entire emergency response pipeline:
1. **Instant Intake:** Citizens report emergencies via an interactive guided AI chatbot in under 60 seconds.
2. **Algorithmic Dispatch:** The system auto-assigns the closest available ambulance, optimal hospital bed (ICU/ER/General), and specialized doctor.
3. **Live Telemetry:** Real-time geospatial GPS tracking on Leaflet maps with live route simulation and ETA countdowns.
4. **Hospital Command Desk:** An executive dashboard for administrators, triage staff, doctors, and fleet operators.

---

## 🛠️ Technology Stack (Kiya Kiya Use Hua Hai)

### 🔹 Backend & Server Architecture
- **Language:** Python 3.10+
- **Framework:** **Flask** (Lightweight, high-performance WSGI web framework)
- **Database ORM:** **Flask-SQLAlchemy** (Object-Relational Mapping for structured models)
- **Database Engine:** **SQLite3** (ACID-compliant relational database, auto-seeded on launch)
- **Security & Authentication:** **Werkzeug Security** (PBKDF2 SHA-256 salted password hashing, role-based session guards)
- **Geospatial Math:** Custom Python implementation of the **Haversine Great-Circle Formula** ($\Delta\sigma$) for calculating exact distances between patient GPS coordinates, ambulances, and hospitals.

### 🔹 Frontend & Human-Computer Interaction (HCI)
- **UI Architecture:** Semantic HTML5 + Vanilla CSS3 (Custom Design System, strictly zero tailwind bloat)
- **CSS Framework:** **Bootstrap 5.3** (Grid & modern responsive utilities)
- **Icons & Typography:** **Bootstrap Icons 1.11**, Google Fonts (**Montserrat**, **Poppins**, **JetBrains Mono**)
- **Client Scripting:** Modern Asynchronous JavaScript (ES6+ Fetch API, DOM manipulation, automated polling without full page reloads)
- **Mapping & GIS:** **Leaflet.js 1.9.4** integrated with OpenStreetMap tiles, custom SVG/CSS vehicle markers with dynamic pulse beacons.
- **HCI Usability Principles:**
  - High data-ink ratio with clean visual hierarchy
  - Fixed 100% width layouts eliminating horizontal scrolling
  - Real-time visual feedback (status beacons, interactive map-to-table cross-focus)
  - Color-coded urgency levels (Critical, High, Medium, Low)

---

## 🚀 Key Features

```
                                  ┌─────────────────────────────┐
                                  │   Citizen Emergency Intake  │
                                  │  (Web Portal / AI Chatbot)  │
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            MedCare Smart Auto-Allocation Engine                             │
│                                                                                             │
│   🚑 Nearest Ambulance (Haversine)   │   🛏️ Bed by Severity   │   👨‍⚕️ Doctor by Keyword NLP │
└──────────────┬───────────────────────────────┬───────────────────────────────┬──────────────┘
               │                               │                               │
               ▼                               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│    Live GPS Fleet Radar     │ │    Hospital Bed Inventory   │ │    Doctor Medical Portal    │
│    (Leaflet Map + ETA)      │ │   (ICU, ER, Gen, Isolation) │ │  (Patient Triage & Intake)  │
└─────────────────────────────┘ └─────────────────────────────┘ └─────────────────────────────┘
```

### 1. 🤖 Guided AI Triage Assistant
- Conversational emergency triage accessible from the persistent bottom widget on any page.
- Collects Patient Name → Age → Symptoms → Priority → Location (GPS or text) → Hospital Preference → Ambulance dispatch.
- Triggers instant automated allocation in a single transaction.

### 2. 🚑 Geospatial Smart Dispatch Algorithm
- **Ambulance:** Calculates real-time distance from patient coordinates to all active 10 fleet units; dispatches the nearest unit within a 20 km radius with realistic travel time calculated at 40 km/h.
- **Bed:** Priority-driven ordered matching:
  - *Critical* $\rightarrow$ ICU $\rightarrow$ Emergency $\rightarrow$ Isolation $\rightarrow$ General
  - *High* $\rightarrow$ Emergency $\rightarrow$ ICU $\rightarrow$ General
  - *Medium / Low* $\rightarrow$ General $\rightarrow$ Emergency
- **Doctor:** Keyword parsing matches symptom descriptions (e.g. *cardiac, chest, breathing, fracture, pediatric*) with physician specialties.

### 3. 🗺️ Live GPS Ambulance Tracking
- **Public Patient Tracker (`/track/<case_code>`):** Dedicated link given to callers to watch their dispatched ambulance arrive in real-time with an active ETA countdown.
- **Admin Fleet Command (`/admin/track`):** All 10 ambulances tracked on a live synchronized tactical radar map with linked status tables. Clicking any vehicle pans the map directly to that unit.

### 4. 🏥 5 Mapped Khairpur Healthcare Centers
- Khairpur Medical Complex (KMC)
- Civil Hospital Khairpur
- Pir Abdul Qadir Shah Jilani Institute
- Lady Dufferin Hospital Khairpur
- Khairpur Emergency Care Center

---

## 👥 Portals & Access Routes

| Portal | URL Path | Intended User | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **Public Portal** | `/` | General Public | Quick emergency call, AI Chatbot assistant, triage guidelines |
| **Request Help** | `/request-help` | Citizens / Relatives | Manual emergency case submission form with GPS auto-detection |
| **Live Case Track**| `/track/<case_code>` | Patients / Callers | Public live vehicle tracking map with real-time ETA |
| **Admin Command** | `/admin` | Dispatch Operators | System KPI stats, active cases, fleet tracker, resource managers |
| **Cases Manager** | `/admin/cases` | Intake Supervisors | Register new intake, priority filtering, discharge/close cases |
| **Fleet Radar** | `/admin/track` | Fleet Dispatchers | Live map of 10 ambulance units, live vehicle GPS telemetry |
| **Resource Desk** | `/admin/resources` | Operations Lead | Live status toggles for beds, on-duty doctors, and ambulance units |
| **Staff Login** | `/login` | Hospital Staff | Direct authenticated entry point for Admin, Doctors, and Drivers |

---

## 🔑 Demo Credentials

> *The database auto-seeds all users, doctors, beds, and vehicles on the very first run.*

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin / Dispatch Desk** | `admin` | `admin123` | Full access to command desk, resources, cases & tracking |
| **Doctor (Cardiology)** | `drsara` | `doctor123` | Dr. Sara Ahmed — Cardiologist |
| **Doctor (Emergency)** | `drbilal` | `doctor123` | Dr. Bilal Shaikh — Emergency Medicine Specialist |
| **Ambulance Driver** | `amb1` | `amb123` | Unit A001 (Advanced Life Support - ALS) |
| **Ambulance Driver** | `amb2` | `amb123` | Unit A002 (Basic Life Support - BLS) |

*(Additional doctor accounts: `drfatima`, `drusman`, `drayesha` · Additional fleet units: `amb3` through `amb10`)*

---

## 🔌 Core REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/ambulance-status` | Returns fleet availability counts (Available, En Route, Occupied, Total) |
| `GET` | `/api/ambulances-live` | Live telemetry of all 10 ambulances with lat/lng, assigned case, and ETA |
| `GET` | `/api/nearby-hospitals?lat=&lng=` | Returns top 3 closest hospitals ranked by distance with free bed counts |
| `POST`| `/api/create-request` | JSON intake API; creates case, triggers auto-allocation, returns case code & tracking URL |
| `GET` | `/api/track/<case_code>` | Real-time position and arrival phase of an individual assigned ambulance |

### Example API Request (cURL):
```bash
curl -X POST http://127.0.0.1:5000/api/create-request \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Zubair Ali",
    "age": 38,
    "condition": "Severe acute chest pain and shortness of breath",
    "priority": "Critical",
    "lat": 27.5320,
    "lng": 68.7590,
    "needs_ambulance": true
  }'
```

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/salmanshamsi925/MedCare-Khairpur-Emergency.git
cd MedCare-Khairpur-Emergency
```

### 2. Set Up Virtual Environment
```bash
# Python Virtual Environment create karein
python -m venv venv

# Activate Environment (Windows):
venv\Scripts\activate

# Activate Environment (macOS/Linux):
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# Alternatively:
pip install flask flask-sqlalchemy
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Platform
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
> *On first run, the SQLite database (`instance/medcare_emergency.db`) is automatically initialized and pre-populated with 5 hospitals, 10 ambulances, 8 beds, 5 doctors, and demo emergency cases.*

---

## 📁 Repository Directory Structure

```text
MedCare-Khairpur-Emergency/
├── app.py                      # Core application: Routes, ORM Models, Allocation Logic, Seeding
├── requirements.txt            # Python dependencies (Flask, Flask-SQLAlchemy)
├── .gitignore                  # Git ignore rules (__pycache__, virtual environments, temp files)
├── README.md                   # Comprehensive project documentation
├── instance/
│   └── medcare_emergency.db    # SQLite database storage
├── static/
│   ├── css/
│   │   └── style.css           # Custom design system (Navy, Red, Yellow, Emerald palettes)
│   ├── favicon.ico             # Brand favicon
│   └── img/
│       ├── logo101.png         # MedCare official logo
│       └── doc101.jpeg         # Staff visual assets
└── templates/
    ├── base.html               # Main Jinja2 layout shell
    ├── index.html              # Landing page with integrated AI Triage Bar
    ├── request_help.html       # Emergency assistance manual intake
    ├── track.html              # Patient public ambulance live map
    ├── login.html              # Staff authentication portal
    ├── admin/
    │   ├── _nav.html           # Dynamic Admin navigation bar
    │   ├── dashboard.html      # Executive Command Center Desk
    │   ├── cases.html          # Emergency cases registry & close action
    │   ├── track.html          # Live 10-unit fleet tactical radar map
    │   ├── resources.html      # Bed, doctor, and vehicle live inventories
    │   └── allocate.html       # Manual smart allocation tester
    ├── doctor/
    │   ├── dashboard.html      # Doctor assigned cases portal
    │   └── patients.html       # Patient clinical history & records
    └── ambulance/
        └── dashboard.html      # Mobile-ready driver dispatch screen
```

---

## 🏆 Hackathon Submission Notes

- **Competition:** OpenHack 2026
- **Team:** HT-03 (**Musafir Devs**)
- **Author:** Salman Ahmed ([@salmanshamsi925](https://github.com/salmanshamsi925))
- **Primary Focus:** Healthcare accessibility, algorithmic dispatch optimization, emergency response time reduction in tier-2 districts (Khairpur, Sindh).

---

## 📄 License
This project is licensed under the **MIT License** — open source and free to adapt for public healthcare innovation.
