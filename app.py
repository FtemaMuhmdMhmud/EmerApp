import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, flash
import logic

app = Flask(__name__)
app.secret_key = "emerapp_cs50_secret_production_key"
DB_NAME = "emergency.db"
SCHEMA_FILE = "schema.sql"


def get_db_connection():
    """إنشاء اتصال مع قاعدة البيانات وإرجاع الصفوف كقواميس لتسهيل الوصول للحقول."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """تهيئة قاعدة البيانات من ملف schema.sql في حال عدم وجود ملف emergency.db مسبقاً."""
    if not os.path.exists(DB_NAME):
        with get_db_connection() as conn:
            if os.path.exists(SCHEMA_FILE):
                with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            conn.commit()


init_db()


@app.route("/", methods=["GET"])
def index():
    """عرض نموذج إدخال بيانات المريض وفحص الطوارئ الأولي."""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """استقبال بيانات المريض، تشغيل خوارزمية الاستبعاد التنازلية، وتخزين النتيجة في SQLite."""
    try:
        patient_name = request.form.get("patient_name", "Anonymous").strip() or "Anonymous"
        age = int(request.form.get("age") or 30)
        gender = request.form.get("gender", "Unspecified")

        patient_data = {
            "hr": request.form.get("hr", 80),
            "sbp": request.form.get("sbp", 120),
            "rr": request.form.get("rr", 16),
            "spo2": request.form.get("spo2", 98),
            "gcs": request.form.get("gcs", 15),
            "arrest": request.form.get("arrest", "no"),
            "bleeding": request.form.get("bleeding", "no"),

            "has_burns": request.form.get("has_burns", "no"),
            "weight": request.form.get("weight", 70),
            "tbsa": request.form.get("tbsa", 0),
            "has_trauma": request.form.get("has_trauma", "no"),

            # محطة الشرايين التاجية (HEART Score)
            "has_chest_pain": request.form.get("has_chest_pain", "no"),
            "heart_h": request.form.get("heart_h", 0),
            "heart_e": request.form.get("heart_e", 0),
            "heart_a": request.form.get("heart_a", 0),
            "heart_r": request.form.get("heart_r", 0),
            "heart_t": request.form.get("heart_t", 0),

            # محطة الجلطة الرئوية (Wells PE)
            "has_dyspnea": request.form.get("has_dyspnea", "no"),
            "wells_dvt": request.form.get("wells_dvt", "no"),
            "wells_pe_first": request.form.get("wells_pe_first", "no"),
            "wells_immob": request.form.get("wells_immob", "no"),
            "wells_prior": request.form.get("wells_prior", "no"),
            "wells_hemoptysis": request.form.get("wells_hemoptysis", "no"),
            "wells_cancer": request.form.get("wells_cancer", "no"),

            "pupils": request.form.get("pupils", "normal"),
            "skin": request.form.get("skin", "normal"),
        }

        summary = logic.evaluate_patient_pipeline(patient_data)
        actions_json = json.dumps(summary["action_plan"])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO patient_cases
                (patient_name, age, gender, triage_color, shock_index, step_reached, action_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_name,
                    age,
                    gender,
                    summary["triage_color"],
                    summary["shock_index"],
                    summary["step_reached"],
                    actions_json,
                ),
            )
            conn.commit()
            case_id = cursor.lastrowid

        return render_template(
            "result.html",
            case_id=case_id,
            patient_name=patient_name,
            age=age,
            gender=gender,
            summary=summary,
        )

    except Exception as e:
        flash(f"Evaluation Error: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/history", methods=["GET"])
def history():
    """عرض سجل الحالات السابقة المخزنة في قاعدة البيانات."""
    with get_db_connection() as conn:
        cases = conn.execute(
            """
            SELECT id, patient_name, age, gender, triage_color, shock_index, step_reached, created_at
            FROM patient_cases
            ORDER BY id DESC
            LIMIT 50
            """
        ).fetchall()
    return render_template("history.html", cases=cases)


@app.route("/case/<int:case_id>", methods=["GET"])
def view_case(case_id):
    """عرض تفاصيل حالة مسجلة مسبقاً من السجل السريري."""
    with get_db_connection() as conn:
        case = conn.execute(
            "SELECT * FROM patient_cases WHERE id = ?", (case_id,)
        ).fetchone()

    if case is None:
        flash("Case ID not found in database.", "warning")
        return redirect(url_for("history"))

    summary = {
        "triage_color": case["triage_color"],
        "shock_index": case["shock_index"],
        "step_reached": case["step_reached"],
        "critical_alerts": [],
        "action_plan": json.loads(case["action_plan"]),
    }

    return render_template(
        "result.html",
        case_id=case["id"],
        patient_name=case["patient_name"],
        age=case["age"],
        gender=case["gender"],
        summary=summary,
    )


if __name__ == "__main__":
    app.run(debug=True)
