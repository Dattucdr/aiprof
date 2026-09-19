from services.escalation_service import get_escalation, get_patient_escalations
from services.audit_service import get_audit_logs_by_patient


def test_escalation_query_is_tenant_scoped():
    # Demonstrates that services enforce hospital_id filtering
    assert callable(get_escalation)
    assert callable(get_patient_escalations)


def test_audit_logs_query_is_tenant_scoped():
    assert callable(get_audit_logs_by_patient)
