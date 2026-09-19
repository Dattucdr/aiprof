from datetime import datetime

from sqlalchemy.orm import Session

from models.call import Call


def append_transcript(
    db: Session,
    call_id: int,
    hospital_id: int,
    speaker: str,
    message: str
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id
        )
        .first()
    )

    if not call:
        raise ValueError("Call not found")

    timestamp = datetime.utcnow().isoformat()

    new_entry = (
        f"[{timestamp}] {speaker}: {message}\n"
    )

    if call.transcript:
        call.transcript += new_entry
    else:
        call.transcript = new_entry

    db.commit()
    db.refresh(call)

    return call


def get_call_transcript(
    db: Session,
    call_id: int,
    hospital_id: int
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id
        )
        .first()
    )

    if not call:
        raise ValueError("Call not found")

    return call.transcript or ""
