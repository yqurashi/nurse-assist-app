from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample patient data
patients = [
    {
        "id": 1,
        "file_no": "1001",
        "name": "John Doe",
        "age": 30,
        "sex": "M",
        "dob": "1993-05-15",
        "observations": {
            "HR": "72",
            "BP": "120/80",
            "O2": "98",
            "CO2": "40",
            "Temp": "36.5",
            "Sx": "Cough",
            "Dx": "Flu",
            "Rx": "Paracetamol"
        },
        "tasks": ["Initial consultation", "Follow-up checkup"]
    }
]

@app.route("/")
def home():
    """Renders the home page with the list of patients."""
    return render_template("home.html", patients=patients)

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    """Handles adding a new patient."""
    if request.method == "POST":
        new_patient = {
            "id": len(patients) + 1,
            "file_no": request.form.get("file_no"),
            "name": request.form.get("name"),
            "age": int(request.form.get("age")),
            "sex": request.form.get("sex"),
            "dob": request.form.get("dob"),
            "observations": {
                "HR": "N/A",
                "BP": "N/A",
                "O2": "N/A",
                "CO2": "N/A",
                "Temp": "N/A",
                "Sx": "",
                "Dx": "",
                "Rx": ""
            },
            "tasks": []
        }
        patients.append(new_patient)
        return redirect("/")
    return render_template("add_patient.html")

@app.route("/patient/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    """Handles editing a patient's information."""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return "Patient not found", 404

    if request.method == "POST":
        # Update patient details
        patient["file_no"] = request.form.get("file_no", patient["file_no"])
        patient["name"] = request.form.get("name", patient["name"])
        patient["age"] = int(request.form.get("age", patient["age"]))
        patient["sex"] = request.form.get("sex", patient["sex"])
        patient["dob"] = request.form.get("dob", patient["dob"])
        return redirect(url_for("home"))

    return render_template("edit_patient.html", patient=patient)

@app.route("/patient/<int:patient_id>/dashboard", methods=["GET", "POST"])
def dashboard(patient_id):
    """Renders the patient dashboard and handles updates."""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return "Patient not found", 404

    # Define normal ranges for observations
    normal_ranges = {
        "HR": (60, 100),
        "BP_systolic": (90, 120),
        "BP_diastolic": (60, 80),
        "O2": (95, 100),
        "Temp": (36.1, 37.2),
        "CO2": (35, 45)
    }

    # Parse observations and handle invalid values
    observations = patient["observations"]
    try:
        HR = float(observations.get("HR", 0))
        BP_values = observations.get("BP", "0/0").split("/")
        BP_systolic = float(BP_values[0])
        BP_diastolic = float(BP_values[1])
        O2 = float(observations.get("O2", 0))
        Temp = float(observations.get("Temp", 0))
        CO2 = float(observations.get("CO2", 0))
    except ValueError:
        HR, BP_systolic, BP_diastolic, O2, Temp, CO2 = 0, 0, 0, 0, 0, 0

    # Determine critical flags
    critical_flags = {
        "HR": not (normal_ranges["HR"][0] <= HR <= normal_ranges["HR"][1]),
        "BP_systolic": not (normal_ranges["BP_systolic"][0] <= BP_systolic <= normal_ranges["BP_systolic"][1]),
        "BP_diastolic": not (normal_ranges["BP_diastolic"][0] <= BP_diastolic <= normal_ranges["BP_diastolic"][1]),
        "O2": not (normal_ranges["O2"][0] <= O2 <= normal_ranges["O2"][1]),
        "Temp": not (normal_ranges["Temp"][0] <= Temp <= normal_ranges["Temp"][1]),
        "CO2": not (normal_ranges["CO2"][0] <= CO2 <= normal_ranges["CO2"][1]),
    }

    if request.method == "POST":
        # Update patient observations
        patient["observations"]["HR"] = request.form.get("HR", "N/A")
        patient["observations"]["BP"] = request.form.get("BP", "N/A")
        patient["observations"]["O2"] = request.form.get("O2", "N/A")
        patient["observations"]["Temp"] = request.form.get("Temp", "N/A")
        patient["observations"]["CO2"] = request.form.get("CO2", "N/A")
        patient["observations"]["Sx"] = request.form.get("Sx", "")
        patient["observations"]["Dx"] = request.form.get("Dx", "")
        patient["observations"]["Rx"] = request.form.get("Rx", "")
        return redirect(url_for("dashboard", patient_id=patient_id))

    return render_template("dashboard.html", patient=patient, critical_flags=critical_flags)

@app.route("/patient/<int:patient_id>/tasks", methods=["POST"])
def manage_tasks(patient_id):
    """Handles task management for a specific patient."""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return "Patient not found", 404

    if "add_task" in request.form:
        # Add a new task
        new_task = request.form.get("new_task")
        if new_task:
            patient["tasks"].append(new_task)

    elif "delete_task" in request.form:
        # Delete the specified task
        task_index = int(request.form.get("delete_task"))
        if 0 <= task_index < len(patient["tasks"]):
            del patient["tasks"][task_index]

    return redirect(url_for("dashboard", patient_id=patient_id))

if __name__ == "__main__":
    app.run(debug=True)
