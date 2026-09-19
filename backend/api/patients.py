from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.patient import Patient
from models.encounter import Encounter
from models.observation import Observation
from models.condition import Condition
from models.medication import Medication
from models.care_plan import CarePlan
from models.procedure import Procedure
from schemas.patient import PatientCreate, PatientResponse
from schemas.encounter import EncounterCreate, EncounterResponse
from schemas.observation import ObservationCreate, ObservationResponse
from schemas.condition import ConditionCreate, ConditionResponse
from schemas.medication import MedicationCreate, MedicationResponse
from schemas.care_plan import CarePlanCreate, CarePlanResponse
from schemas.procedure import ProcedureCreate, ProcedureResponse
from schemas.discharge import DischargeResponse
from schemas.timeline import TimelineItem

from auth.dependencies import get_current_user
from auth.roles import UserRole
from models.user import User
from core.tenant import get_tenant_id


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(
    patient_data: PatientCreate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = Patient(
        hospital_id=hospital_id,
        **patient_data.model_dump()
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get(
    "",
    response_model=list[PatientResponse]
)
def get_patients(
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patients = db.query(Patient).filter(
        Patient.hospital_id == hospital_id,
        Patient.is_active == True
    ).all()

    return patients


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


@router.post(
    "/{patient_id}/encounters",
    response_model=EncounterResponse,
    status_code=status.HTTP_201_CREATED
)
def create_encounter(
    patient_id: int,
    encounter_data: EncounterCreate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    encounter = Encounter(
        patient_id=patient_id,
        hospital_id=hospital_id,
        **encounter_data.model_dump()
    )

    db.add(encounter)
    db.commit()
    db.refresh(encounter)

    return encounter


@router.get(
    "/{patient_id}/encounters",
    response_model=list[EncounterResponse]
)
def get_patient_encounters(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id,
        Encounter.hospital_id == hospital_id
    ).all()

    return encounters


@router.post(
    "/{patient_id}/observations",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_observation(
    patient_id: int,
    observation_data: ObservationCreate,
    encounter_id: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if encounter_id is not None:
        encounter = db.query(Encounter).filter(
            Encounter.id == encounter_id,
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        ).first()

        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encounter not found"
            )

    observation = Observation(
        patient_id=patient_id,
        hospital_id=hospital_id,
        encounter_id=encounter_id,
        **observation_data.model_dump()
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    return observation


@router.get(
    "/{patient_id}/observations",
    response_model=list[ObservationResponse]
)
def get_patient_observations(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    observations = db.query(Observation).filter(
        Observation.patient_id == patient_id,
        Observation.hospital_id == hospital_id
    ).all()

    return observations


@router.post(
    "/{patient_id}/conditions",
    response_model=ConditionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_condition(
    patient_id: int,
    condition_data: ConditionCreate,
    encounter_id: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if encounter_id is not None:
        encounter = db.query(Encounter).filter(
            Encounter.id == encounter_id,
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        ).first()

        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encounter not found"
            )

    condition = Condition(
        patient_id=patient_id,
        hospital_id=hospital_id,
        encounter_id=encounter_id,
        **condition_data.model_dump()
    )

    db.add(condition)
    db.commit()
    db.refresh(condition)

    return condition


@router.get(
    "/{patient_id}/conditions",
    response_model=list[ConditionResponse]
)
def get_patient_conditions(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    conditions = db.query(Condition).filter(
        Condition.patient_id == patient_id,
        Condition.hospital_id == hospital_id
    ).all()

    return conditions


@router.post(
    "/{patient_id}/medications",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_medication(
    patient_id: int,
    medication_data: MedicationCreate,
    encounter_id: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if encounter_id is not None:
        encounter = db.query(Encounter).filter(
            Encounter.id == encounter_id,
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        ).first()

        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encounter not found"
            )

    medication = Medication(
        patient_id=patient_id,
        hospital_id=hospital_id,
        encounter_id=encounter_id,
        **medication_data.model_dump()
    )

    db.add(medication)
    db.commit()
    db.refresh(medication)

    return medication


@router.get(
    "/{patient_id}/medications",
    response_model=list[MedicationResponse]
)
def get_patient_medications(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    medications = db.query(Medication).filter(
        Medication.patient_id == patient_id,
        Medication.hospital_id == hospital_id
    ).all()

    return medications


@router.post(
    "/{patient_id}/care-plans",
    response_model=CarePlanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_care_plan(
    patient_id: int,
    care_plan_data: CarePlanCreate,
    encounter_id: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if encounter_id is not None:
        encounter = db.query(Encounter).filter(
            Encounter.id == encounter_id,
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        ).first()

        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encounter not found"
            )

    care_plan = CarePlan(
        patient_id=patient_id,
        hospital_id=hospital_id,
        encounter_id=encounter_id,
        **care_plan_data.model_dump()
    )

    db.add(care_plan)
    db.commit()
    db.refresh(care_plan)

    return care_plan


@router.get(
    "/{patient_id}/care-plans",
    response_model=list[CarePlanResponse]
)
def get_patient_care_plans(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    care_plans = db.query(CarePlan).filter(
        CarePlan.patient_id == patient_id,
        CarePlan.hospital_id == hospital_id
    ).all()

    return care_plans


@router.post(
    "/{patient_id}/procedures",
    response_model=ProcedureResponse,
    status_code=status.HTTP_201_CREATED
)
def create_procedure(
    patient_id: int,
    procedure_data: ProcedureCreate,
    encounter_id: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if encounter_id is not None:
        encounter = db.query(Encounter).filter(
            Encounter.id == encounter_id,
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        ).first()

        if not encounter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Encounter not found"
            )

    procedure = Procedure(
        patient_id=patient_id,
        hospital_id=hospital_id,
        encounter_id=encounter_id,
        **procedure_data.model_dump()
    )

    db.add(procedure)
    db.commit()
    db.refresh(procedure)

    return procedure


@router.get(
    "/{patient_id}/procedures",
    response_model=list[ProcedureResponse]
)
def get_patient_procedures(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    procedures = db.query(Procedure).filter(
        Procedure.patient_id == patient_id,
        Procedure.hospital_id == hospital_id
    ).all()

    return procedures


@router.get(
    "/{patient_id}/discharge",
    response_model=DischargeResponse
)
def get_patient_discharge(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    encounter = db.query(Encounter).filter(
        Encounter.patient_id == patient_id,
        Encounter.hospital_id == hospital_id,
        Encounter.discharge_datetime.is_not(None)
    ).order_by(
        Encounter.discharge_datetime.desc()
    ).first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No discharge record found"
        )

    return {
        "patient_id": patient_id,
        "encounter_id": encounter.id,
        "admission_datetime": encounter.admission_datetime,
        "discharge_datetime": encounter.discharge_datetime,
        "discharge_status": encounter.discharge_status,
        "discharge_instructions": encounter.discharge_instructions
    }


@router.get(
    "/{patient_id}/timeline",
    response_model=list[TimelineItem]
)
def get_patient_timeline(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    timeline = []

    encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id,
        Encounter.hospital_id == hospital_id
    ).all()

    for encounter in encounters:
        timeline.append(
            TimelineItem(
                event_type="ENCOUNTER",
                event_id=encounter.id,
                event_datetime=encounter.admission_datetime,
                title=encounter.encounter_type,
                description=encounter.reason
            )
        )

    observations = db.query(Observation).filter(
        Observation.patient_id == patient_id,
        Observation.hospital_id == hospital_id
    ).all()

    for observation in observations:
        timeline.append(
            TimelineItem(
                event_type="OBSERVATION",
                event_id=observation.id,
                event_datetime=observation.observed_at,
                title=observation.observation_type,
                description=f"{observation.value} {observation.unit or ''}".strip()
            )
        )

    conditions = db.query(Condition).filter(
        Condition.patient_id == patient_id,
        Condition.hospital_id == hospital_id
    ).all()

    for condition in conditions:
        timeline.append(
            TimelineItem(
                event_type="CONDITION",
                event_id=condition.id,
                event_datetime=condition.onset_date,
                title=condition.condition_name,
                description=condition.description
            )
        )

    medications = db.query(Medication).filter(
        Medication.patient_id == patient_id,
        Medication.hospital_id == hospital_id
    ).all()

    for medication in medications:
        timeline.append(
            TimelineItem(
                event_type="MEDICATION",
                event_id=medication.id,
                event_datetime=medication.start_date,
                title=medication.medication_name,
                description=medication.instructions
            )
        )

    care_plans = db.query(CarePlan).filter(
        CarePlan.patient_id == patient_id,
        CarePlan.hospital_id == hospital_id
    ).all()

    for care_plan in care_plans:
        timeline.append(
            TimelineItem(
                event_type="CARE_PLAN",
                event_id=care_plan.id,
                event_datetime=care_plan.start_date,
                title=care_plan.title,
                description=care_plan.follow_up_instructions
            )
        )

    procedures = db.query(Procedure).filter(
        Procedure.patient_id == patient_id,
        Procedure.hospital_id == hospital_id
    ).all()

    for procedure in procedures:
        timeline.append(
            TimelineItem(
                event_type="PROCEDURE",
                event_id=procedure.id,
                event_datetime=procedure.performed_at,
                title=procedure.procedure_name,
                description=procedure.notes
            )
        )

    timeline.sort(
        key=lambda item: item.event_datetime or datetime.min,
        reverse=True
    )

    return timeline








