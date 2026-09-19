from workers.celery_app import celery_app
from database.database import SessionLocal

from models.outreach_documentation import (
    OutreachDocumentation,
)
from services.ehr_documentation_service import (
    write_outreach_note_to_mock_ehr,
)


@celery_app.task(
    name="write_documentation_to_ehr"
)
def write_documentation_to_ehr(
    documentation_id: int,
):
    db = SessionLocal()

    try:
        documentation = (
            db.query(
                OutreachDocumentation
            )
            .filter(
                OutreachDocumentation.id
                == documentation_id
            )
            .first()
        )

        if not documentation:
            raise ValueError(
                "Documentation not found"
            )

        result = (
            write_outreach_note_to_mock_ehr(
                db=db,
                hospital_id=(
                    documentation.hospital_id
                ),
                patient_id=(
                    documentation.patient_id
                ),
                documentation=documentation,
            )
        )

        return result

    finally:
        db.close()
