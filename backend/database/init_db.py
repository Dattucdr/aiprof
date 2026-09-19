from database.database import Base, engine

from models.hospital import Hospital
from models.user import User
from models.patient import Patient
from models.encounter import Encounter
from models.observation import Observation
from models.condition import Condition
from models.medication import Medication
from models.care_plan import CarePlan
from models.procedure import Procedure
from models.campaign import Campaign
from models.queue_item import QueueItem
from models.call import Call
from models.escalation import Escalation
from models.triage_assessment import TriageAssessment
from models.consensus_assessment import ConsensusAssessment
from models.outreach_documentation import OutreachDocumentation
from models.escalation_assessment import EscalationAssessment
from models.audit_log import AuditLog
from models.ai_execution import AIExecution


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()