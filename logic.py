import math

def evaluate_patient_pipeline(data):
    """
    الدالة الشاملة التي تستقبل بيانات المريض وتمررها على شجرة الاستبعاد التنازلية
    (Triage -> Trauma/Burns -> ACS -> PE -> Toxicology & Metabolic).
    """
    summary = {
        "triage_color": "GREEN",
        "shock_index": 0.0,
        "critical_alerts": [],
        "step_reached": "Stable / Undifferentiated",
        "action_plan": []
    }

    hr = float(data.get("hr") or 80)
    sbp = float(data.get("sbp") or 120)
    rr = float(data.get("rr") or 16)
    spo2 = float(data.get("spo2") or 98)
    gcs = float(data.get("gcs") or 15)
    is_arrest = str(data.get("arrest", "")).lower() == "yes"
    active_bleeding = str(data.get("bleeding", "")).lower() == "yes"

    shock_index = round(hr / sbp, 2) if sbp > 0 else 0.0
    summary["shock_index"] = shock_index

    if is_arrest:
        summary["triage_color"] = "RED"
        summary["step_reached"] = "Cardiac Arrest Protocol"
        summary["action_plan"] = [
            "Immediate high-quality chest compressions (100-120 bpm, 30:2 ratio).",
            "Attach Defibrillator/Monitor: Assess for VF/pVT (Shockable) vs PEA/Asystole.",
            "Epinephrine 1 mg IV/IO every 3-5 minutes + Advanced Airway placement."
        ]
        return summary

    if gcs <= 8 or shock_index >= 1.0 or spo2 < 90 or sbp < 90 or active_bleeding:
        summary["triage_color"] = "RED"
        summary["critical_alerts"].append("Hemodynamic Instability / Airway Compromise")
        if gcs <= 8:
            summary["action_plan"].append("Airway Protection: Immediate Endotracheal Intubation (GCS <= 8).")
        if shock_index >= 1.0 or active_bleeding:
            summary["action_plan"].append(
                f"Severe Shock State (SI: {shock_index}): Push 2 large-bore IVs (16G) + 1L warmed crystalloid / MTP activation."
            )
        if spo2 < 90:
            summary["action_plan"].append("Severe Hypoxia: Place 15 L/min O2 via Non-Rebreather Mask immediately.")

    has_burns = str(data.get("has_burns", "")).lower() == "yes"
    has_trauma = str(data.get("has_trauma", "")).lower() == "yes"

    if has_burns:
        summary["step_reached"] = "Burn Resuscitation Protocol"
        weight = float(data.get("weight") or 70)
        tbsa = float(data.get("tbsa") or 0)
        total_fluids = 4.0 * weight * tbsa
        rate_first_8h = (total_fluids / 2.0) / 8.0 if total_fluids > 0 else 0
        rate_next_16h = (total_fluids / 2.0) / 16.0 if total_fluids > 0 else 0

        summary["action_plan"].append(
            f"Parkland Resuscitation: Total 24h Crystalloids = {int(total_fluids)} mL Ringer's Lactate. "
            f"Infuse {int(rate_first_8h)} mL/h for the first 8 hours, then {int(rate_next_16h)} mL/h for the remaining 16 hours."
        )
        return summary

    if has_trauma:
        summary["step_reached"] = "Trauma Evaluation (RTS)"
        c_gcs = 4 if gcs >= 13 else (3 if gcs >= 9 else (2 if gcs >= 6 else (1 if gcs >= 4 else 0)))
        c_sbp = 4 if sbp > 89 else (3 if sbp >= 76 else (2 if sbp >= 50 else (1 if sbp >= 1 else 0)))
        c_rr = 4 if 10 <= rr <= 29 else (3 if rr > 29 else (2 if 6 <= rr <= 9 else (1 if 1 <= rr <= 5 else 0)))
        rts = round((0.9368 * c_gcs) + (0.7326 * c_sbp) + (0.2908 * c_rr), 2)

        outcome = "Critical (< 30% survival)" if rts < 4.0 else ("Severe" if rts < 6.0 else "Stable (> 90% survival)")
        summary["action_plan"].append(
            f"Revised Trauma Score (RTS): {rts} ({outcome}). Proceed with ATLS Secondary Survey and eFAST scan."
        )
        return summary

    has_chest_pain = str(data.get("has_chest_pain", "")).lower() == "yes"
    if has_chest_pain:
        h = int(data.get("heart_h") or 0)
        e = int(data.get("heart_e") or 0)
        a = int(data.get("heart_a") or 0)
        r = int(data.get("heart_r") or 0)
        t = int(data.get("heart_t") or 0)
        heart_total = h + e + a + r + t

        if heart_total >= 4:
            summary["step_reached"] = "Acute Coronary Syndrome Suspected"
            if heart_total >= 7:
                summary["triage_color"] = "RED"
                summary["action_plan"].append(
                    f"HEART Score: {heart_total} (High Risk). Activate Emergency Cath Lab, Aspirin 300mg, P2Y12 inhibitor, UFH bolus."
                )
            else:
                if summary["triage_color"] != "RED":
                    summary["triage_color"] = "YELLOW"
                summary["action_plan"].append(
                    f"HEART Score: {heart_total} (Intermediate Risk). Admit to Clinical Decision Unit: Serial High-Sensitivity Troponins & continuous ECG."
                )
            return summary
        else:
            summary["critical_alerts"].append(
                f"ACS Ruled Low-Risk (HEART Score: {heart_total} <= 3). Proceeding to Pulmonology ladder."
            )

    has_dyspnea = str(data.get("has_dyspnea", "")).lower() == "yes"
    if has_dyspnea:
        wells_score = 0.0
        if str(data.get("wells_dvt", "")).lower() == "yes": wells_score += 3.0
        if str(data.get("wells_pe_first", "")).lower() == "yes": wells_score += 3.0
        if hr > 100: wells_score += 1.5
        if str(data.get("wells_immob", "")).lower() == "yes": wells_score += 1.5
        if str(data.get("wells_prior", "")).lower() == "yes": wells_score += 1.5
        if str(data.get("wells_hemoptysis", "")).lower() == "yes": wells_score += 1.0
        if str(data.get("wells_cancer", "")).lower() == "yes": wells_score += 1.0

        if wells_score > 4.0:
            summary["step_reached"] = "Pulmonary Embolism Likely"
            if summary["triage_color"] != "RED":
                summary["triage_color"] = "YELLOW"
            summary["action_plan"].append(
                f"Wells' PE Score: {wells_score} (PE Likely). Urgent CT Pulmonary Angiogram (CTPA) required. Empiric therapeutic anticoagulation."
            )
            return summary
        else:
            summary["critical_alerts"].append(
                f"PE Unlikely (Wells' Score: {wells_score} <= 4). Order High-Sensitivity D-dimer. Proceeding to Toxicology ladder."
            )

    pupils = str(data.get("pupils", "normal")).strip().lower()
    skin = str(data.get("skin", "normal")).strip().lower()
    summary["step_reached"] = "Toxicology & Metabolic Assessment"

    if pupils == "pinpoint" and skin != "sweaty":
        if summary["triage_color"] == "GREEN":
            summary["triage_color"] = "YELLOW"
        summary["action_plan"].append(
            "Suspected Opioid Toxidrome (Miosis present): Administer Naloxone 0.4 - 2.0 mg IV/IM. Titrate immediately to restore adequate spontaneous respiratory effort."
        )

    elif pupils == "pinpoint" and skin == "sweaty":
        summary["triage_color"] = "RED"
        summary["action_plan"].append(
            "Suspected Cholinergic Toxidrome (e.g. Organophosphates / Nerve Agent): Administer Atropine 2 mg IV every 5 min until pulmonary secretions dry + Pralidoxime."
        )

    elif pupils == "dilated" and skin == "dry" and hr > 100:
        if summary["triage_color"] == "GREEN":
            summary["triage_color"] = "YELLOW"
        summary["action_plan"].append(
            "Suspected Anticholinergic Toxicity: Supportive care, active external cooling, continuous telemetry, consider Physostigmine for severe refractory delirium."
        )

    elif pupils == "dilated" and skin == "sweaty" and hr > 100:
        if summary["triage_color"] == "GREEN":
            summary["triage_color"] = "YELLOW"
        summary["action_plan"].append(
            "Suspected Sympathomimetic Toxicity (Cocaine / Amphetamines): Administer Benzodiazepines (Diazepam 5-10 mg IV), aggressive cooling. Avoid pure beta-blockers."
        )

    else:
        summary["action_plan"].append(
            "Undifferentiated Altered Mental Status: Check Point-of-Care Capillary Glucose immediately (Rule out Hypoglycemia) + Send Basic Metabolic Panel & ABG."
        )

    return summary
