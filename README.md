# EmerApp: Clinical Decision Support & Emergency Triage Suite

#### Video Demo: (https://youtu.be/J8nB8VKf86c)]

#### Description: EmerApp too for Emergency Approach to assess the full situation of patient - for CS50x - presented by Fatema Muhamad Mahmoud an Intern Doctor at Aswan University Hospitals

**EmerApp** is a web-based clinical decision support tool and algorithmic triage suite built using Python (Flask), SQLite, and Bootstrap 5. Developed as a final project for CS50x, the application translates complex clinical reasoning, vital sign analytics, and emergency medicine algorithms into an interactive, deterministic diagnostic workflow. It models real-world emergency department workflows by establishing a sequential "Exclusion Ladder" protocol to rapidly identify, triage, and manage acute medical emergencies.

---

### Project Motivation & Clinical Vision

In high-acuity emergency departments, cognitive overload, rapid patient turnover, and diagnostic delays can directly lead to preventable morbidity and mortality. Junior doctors, emergency medical technicians, and triage nurses must rapidly synthesize physiological markers, recognize life-threatening patterns, and initiate resuscitation within minutes of patient presentation.

Traditional medical calculators often operate in isolation: a clinician must navigate to one page for the Glasgow Coma Scale, another for the HEART Score, and yet another for burn fluid calculations. **EmerApp** unifies these disjointed tools into a centralized, streamlined pipeline. Rather than forcing the clinician to guess which pathway to open, the application evaluates vital signs and categorical symptoms systematically, ruling out immediate threats to life before moving down the clinical hierarchy.

---

### Key Clinical Algorithms & Mathematical Logic

The core computational logic of EmerApp resides in `logic.py`, which executes a sequential exclusion pipeline:

1. **Hemodynamic Instability & Rapid ABC Triage:**
   The application immediately computes the **Shock Index (SI)**:
   $$\text{Shock Index} = \frac{\text{Heart Rate (HR)}}{\text{Systolic Blood Pressure (SBP)}}$$
   A Shock Index $\ge 1.0$ indicates significant hypoperfusion, occult hemorrhage, or early septic shock, immediately elevating the patient to **CODE RED (Resuscitation)** status. Airway compromise ($\text{GCS} \le 8$), profound hypoxia ($\text{SpO}_2 < 90\%$), active exsanguination, or cardiac arrest will trigger rapid-sequence intubation alerts, massive transfusion protocols (MTP), and immediate ACLS algorithms.

2. **Trauma & Burn Resuscitation:**
   * **Parkland Formula:** Calculates 24-hour crystalloid requirements for significant thermal burns:
     $$\text{Volume (mL)} = 4 \times \text{Weight (kg)} \times \text{TBSA (\% Second/Third Degree)}$$
     The code automatically splits the volume, outputting precise infusion rates in mL/hour for the first 8 hours versus the remaining 16 hours.
   * **Revised Trauma Score (RTS):** Computes physiological trauma scoring based on coded parameters for GCS, SBP, and respiratory rate using standard weighted logistic coefficients:
     $$\text{RTS} = 0.9368(\text{cGCS}) + 0.7326(\text{cSBP}) + 0.2908(\text{cRR})$$

3. **Acute Coronary Syndrome (ACS) Exclusion Ladder:**
   Integrates the validated **HEART Score** (History, ECG, Age, Risk Factors, Troponin). Scores $\ge 7$ trigger emergency catheterization lab activation, intermediate scores ($4-6$) trigger telemetry admission and serial biomarkers, while scores $\le 3$ safely rule out acute coronary syndrome and allow the ladder to progress.

4. **Pulmonary Embolism (PE) Exclusion Ladder:**
   Implements **Wells' Criteria for PE**. Patients with scores $> 4.0$ are classified as "PE Likely" and routed directly to Computed Tomography Pulmonary Angiography (CTPA) and empiric anticoagulation, whereas scores $\le 4.0$ mandate high-sensitivity D-dimer testing.

5. **Toxicology & Neurometabolic Profiling:**
   When structural and cardiopulmonary emergencies are cleared in an uncommunicative or obtunded patient, the system cross-references pupillary signs (pinpoint vs. dilated) and autonomic dermatological features (diaphoresis vs. anhidrosis) against physiological vitals. This identifies classic toxidromes—such as Opioid, Cholinergic (organophosphate), Anticholinergic, and Sympathomimetic overdoses—and suggests specific antidotes (e.g., Naloxone, Atropine, or Benzodiazepines).

---

### Project Architecture & File Breakdown

The repository is intentionally architected according to separation-of-concerns principles, keeping database persistence, clinical reasoning, and route presentation decoupled:

* **`app.py`:**
  The primary controller of the Flask application. It defines HTTP endpoints (`/`, `/evaluate`, `/history`, `/case/<id>`), handles incoming `POST` requests from the patient admission form, parses incoming data types, invokes the clinical pipeline, commits evaluated encounters into the database, and renders appropriate Jinja templates.

* **`logic.py`:**
  The computational heart of the software. It contains pure Python mathematical and conditional algorithms. Keeping `logic.py` devoid of database and web dependencies ensures that the clinical engine can be independently unit-tested and easily maintained.

* **`schema.sql`:**
  Defines the relational SQLite database architecture. It builds the `patient_cases` table to log patient demographics, assigned triage colors (`RED`, `YELLOW`, `GREEN`), numeric shock indices, dominant diagnostic paths, serialized JSON action plans, and automatic timestamps. It also creates database indices on `created_at` and `triage_color` to optimize audit queries.

* **`init_db.py`:**
  A dedicated setup script that reads `schema.sql` and initializes `emergency.db` cleanly.

* **`templates/layout.html`:**
  The master Jinja template. It sets up metadata, responsive viewports, Bootstrap 5 styling, Bootstrap Icons, system alerts/flashes, and the standard emergency department navigation header.

* **`templates/index.html`:**
  The central patient admission interface. It is organized into logical clinical cards (Demographics, Baseline Vitals, Trauma/Burn Screener, Chest Pain/HEART form, Dyspnea/Wells form, and Toxicology inspection).

* **`templates/result.html`:**
  The Clinical Action Report. It dynamically themes its primary banner based on triage acuity (Danger Red, Warning Yellow, or Success Green), displays numeric indices, details an ordered list of actionable medical directives, and visualizes an exclusion ladder audit showing which conditions were ruled in or ruled out.

* **`templates/history.html`:**
  The emergency department clinical logbook. It tabularizes historical admissions stored in `emergency.db`, displaying acuity badges, timestamps, and quick-access review links.

* **`static/style.css`:**
  Minimal, clean CSS extensions augmenting Bootstrap to deliver a modern clinical UI with custom font smoothing and typographic spacing.

* **`requirements.txt`:**
  Lists Python dependencies required to run the project.

---

### Design Decisions & Engineering Trade-offs

* **Monolithic Multi-Stage Form vs. Multi-Page Wizard:**
  In real emergency department triage, clinicians do not have time to click through a multi-step wizard to see a result. A single-page input with grouped semantic sections was chosen to minimize input latency.
* **Server-Side Clinical Validation (Python) vs. Client-Side (JavaScript):**
  While client-side scripts can compute scores dynamically, critical medical calculations were centralized inside `logic.py` on the Flask server. This ensures data integrity, deterministic outputs, and auditable database storage for every calculated case.
* **JSON Serialization for Clinical Directives:**
  The `action_plan` generated by the clinical engine is serialized as a JSON string inside the SQLite database. This allows variable numbers of diagnostic recommendations to be stored without introducing relational bloat across multiple joined tables.

---

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone (https://github.com/FtemaMuhmdMhmud/EmerApp.git)
   cd EmerApp
