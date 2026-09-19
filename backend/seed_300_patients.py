"""
Create 300 synthetic patients + discharged encounters for the AIProf demo.

Run from project root:
    $env:PYTHONPATH="backend"
    python seed_300_patients.py

Optional hospital ID:
    $env:HOSPITAL_ID="1"
"""

import os
from datetime import datetime, timedelta

from database.database import SessionLocal
from models.patient import Patient
from models.encounter import Encounter

HOSPITAL_ID = int(os.getenv("HOSPITAL_ID", "1"))
COUNT = 300

first_names = [
    "Aarav","Vivaan","Aditya","Arjun","Rahul","Kiran","Rohan","Vikram",
    "Sanjay","Nikhil","Ananya","Diya","Isha","Priya","Sneha","Kavya",
    "Meera","Pooja","Neha","Aisha"
]
last_names = [
    "Sharma","Reddy","Rao","Patel","Kumar","Verma","Singh","Naidu",
    "Iyer","Gupta","Das","Mishra","Joshi","Nair","Menon","Bose",
    "Varma","Chowdary","Bhat","Reddy"
]
languages = ["English", "Telugu", "Hindi"]
call_times = ["09:00","10:00","11:00","14:00","15:00","16:00","17:00"]

db = SessionLocal()

try:
    created = 0
    skipped = 0
    now = datetime.utcnow()

    for i in range(1, COUNT + 1):
        mrn = f"DEMO-{i:04d}"

        existing = (
            db.query(Patient)
            .filter(
                Patient.hospital_id == HOSPITAL_ID,
                Patient.medical_record_number == mrn
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        patient = Patient(
            hospital_id=HOSPITAL_ID,
            medical_record_number=mrn,
            first_name=first_names[(i - 1) % len(first_names)],
            last_name=last_names[((i - 1) // len(first_names)) % len(last_names)],
            date_of_birth=datetime(
                now.year - (25 + (i % 58)),
                ((i - 1) % 12) + 1,
                ((i - 1) % 28) + 1
            ),
            gender="Male" if i % 2 else "Female",
            phone_number=f"+9199{10000000 + i:08d}",
            email=f"demo.patient{i:03d}@example.com",
            communication_consent=True,
            preferred_language=languages[(i - 1) % len(languages)],
            preferred_call_time=call_times[(i - 1) % len(call_times)],
            is_active=True
        )

        db.add(patient)
        db.flush()

        # Spread discharge dates across the 1-6 day eligibility window.
        discharge_days_ago = ((i - 1) % 6) + 1
        discharge_dt = now - timedelta(days=discharge_days_ago)

        encounter = Encounter(
            patient_id=patient.id,
            hospital_id=HOSPITAL_ID,
            encounter_type="INPATIENT",
            admission_datetime=discharge_dt - timedelta(days=2 + (i % 4)),
            discharge_datetime=discharge_dt,
            discharge_status="DISCHARGED",
            reason="Synthetic post-discharge demo encounter",
            discharge_instructions=(
                "Synthetic demo record. Follow the configured "
                "post-discharge outreach protocol."
            )
        )

        db.add(encounter)
        created += 1

        if created % 50 == 0:
            db.commit()
            print(f"Created {created}/{COUNT} patients...")

    db.commit()

    print("\n300-patient demo dataset ready.")
    print(f"Created: {created}")
    print(f"Skipped existing: {skipped}")

finally:
    db.close()
