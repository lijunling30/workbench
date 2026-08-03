"""M1 项目管理：CRUD + 项目成本统计 + 预算。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, User
from ..schemas import Msg, ProjectIn, ProjectOut
from ..services.auth import get_current_user
from ..services.cost import project_cost, check_budget

router = APIRouter(prefix="/projects", tags=["项目管理"])


def _owned(db: Session, project_id: int, user: User) -> Project:
    p = db.get(Project, project_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="项目不存在")
    return p


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Project).filter(Project.user_id == user.id).order_by(Project.id.desc()).all()


@router.post("", response_model=ProjectOut)
def create_project(data: ProjectIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = Project(user_id=user.id, **data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _owned(db, project_id, user)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _owned(db, project_id, user)
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{project_id}", response_model=Msg)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _owned(db, project_id, user)
    db.delete(p)
    db.commit()
    return Msg(message="项目已删除")


@router.get("/{project_id}/costs")
def project_costs(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _owned(db, project_id, user)
    return check_budget(db, _owned(db, project_id, user))
