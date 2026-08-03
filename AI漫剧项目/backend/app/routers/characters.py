"""M5 角色资产库：人物子库 + 角色维护。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Character, CharacterLibrary, User
from ..schemas import CharacterIn, CharacterOut, LibraryIn, LibraryOut
from ..services.auth import get_current_user
from ..services import pipeline

router = APIRouter(prefix="/character", tags=["角色资产库"])


@router.get("/libraries", response_model=list[LibraryOut])
def list_libraries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(CharacterLibrary).filter(CharacterLibrary.user_id == user.id).all()


@router.post("/libraries", response_model=LibraryOut)
def create_library(data: LibraryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lib = CharacterLibrary(user_id=user.id, **data.model_dump())
    db.add(lib)
    db.commit()
    db.refresh(lib)
    return lib


@router.post("/libraries/{lib_id}/duplicate", response_model=LibraryOut)
def duplicate_library(lib_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    src = db.get(CharacterLibrary, lib_id)
    if not src or src.user_id != user.id:
        raise HTTPException(status_code=404, detail="子库不存在")
    new = CharacterLibrary(user_id=user.id, name=f"{src.name}（副本）", desc=src.desc,
                           project_ids=list(src.project_ids), is_shared=False)
    db.add(new)
    db.commit()
    db.refresh(new)
    for ch in db.query(Character).filter(Character.library_id == src.id):
        db.add(Character(library_id=new.id, name=ch.name, desc=ch.desc,
                         ref_images=list(ch.ref_images), expression_set=list(ch.expression_set)))
    db.commit()
    return new


@router.delete("/libraries/{lib_id}")
def delete_library(lib_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lib = db.get(CharacterLibrary, lib_id)
    if not lib or lib.user_id != user.id:
        raise HTTPException(status_code=404, detail="子库不存在")
    db.query(Character).filter(Character.library_id == lib_id).delete()
    db.delete(lib)
    db.commit()
    return {"message": "子库已删除"}


@router.get("/libraries/{lib_id}/characters", response_model=list[CharacterOut])
def list_characters(lib_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Character).filter(Character.library_id == lib_id).all()


@router.post("/characters", response_model=CharacterOut)
def create_character(data: CharacterIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lib = db.get(CharacterLibrary, data.library_id)
    if not lib or lib.user_id != user.id:
        raise HTTPException(status_code=404, detail="子库不存在")
    ch = Character(library_id=data.library_id, name=data.name, desc=data.desc)
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


@router.post("/characters/{char_id}/images", response_model=CharacterOut)
def generate_character_images(char_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """为角色生成三视图 + 表情集（当前 Mock 生成占位图）。"""
    ch = db.get(Character, char_id)
    if not ch:
        raise HTTPException(status_code=404, detail="角色不存在")
    return pipeline.execute_character_images(db, user, char_id)
