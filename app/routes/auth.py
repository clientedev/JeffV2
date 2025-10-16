from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, Token
from app.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "funcao": user.funcao}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    new_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        funcao=usuario.funcao
    )
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    return new_usuario

@router.get("/usuarios/me", response_model=UsuarioResponse)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.get("/usuarios", response_model=list[UsuarioResponse])
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("Admin"))
):
    usuarios = db.query(Usuario).all()
    return usuarios
