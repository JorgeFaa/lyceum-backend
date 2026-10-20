from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models.note import Note
from app.db.models.subject import Subject
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.subject import SubjectCreate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Subject]:
    return db.query(Subject).filter(Subject.user_id == current_user.id).all()


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    request: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Subject:
    existing = (
        db.query(Subject)
        .filter(Subject.user_id == current_user.id, Subject.name == request.name)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una asignatura con ese nombre")

    subject = Subject(user_id=current_user.id, name=request.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == current_user.id)
        .first()
    )
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")

    has_notes = db.query(Note).filter(Note.subject_id == subject_id).first() is not None
    if has_notes:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La asignatura tiene apuntes asociados")

    db.delete(subject)
    db.commit()
    return {"deleted": True}
