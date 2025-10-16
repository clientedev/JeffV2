from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from app.database import get_db, init_db, engine
from app.models.models import Usuario
from app.auth import get_current_user
from app.routes import auth, empresas, consultores, propostas, cronogramas, contratos, bi, importacao, chatbot, relatorios, alertas

app = FastAPI(
    title="Sistema de relacionamento com a industria",
    version="1.03"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/api", tags=["Autenticação"])
app.include_router(empresas.router, prefix="/api/empresas", tags=["Empresas"])
app.include_router(consultores.router, prefix="/api/consultores", tags=["Consultores"])
app.include_router(propostas.router, prefix="/api/propostas", tags=["Propostas"])
app.include_router(cronogramas.router, prefix="/api/cronogramas", tags=["Cronogramas"])
app.include_router(contratos.router, prefix="/api/contratos", tags=["Contratos"])
app.include_router(bi.router, prefix="/api/bi", tags=["Business Intelligence"])
app.include_router(importacao.router, prefix="/api/importacao", tags=["Importação"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
app.include_router(alertas.router, prefix="/api/alertas", tags=["Alertas"])

@app.on_event("startup")
async def startup_event():
    init_db()
    db = next(get_db())
    
    admin_email = os.getenv("ADMIN_EMAIL", "admin@sistema.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    admin_exists = db.query(Usuario).filter(Usuario.email == admin_email).first()
    if not admin_exists:
        from app.auth import get_password_hash
        admin = Usuario(
            nome="Administrador",
            email=admin_email,
            senha_hash=get_password_hash(admin_password),
            funcao="Admin"
        )
        db.add(admin)
        db.commit()
        print(f"✓ Usuário admin criado com email: {admin_email}")
    
    db.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/alertas", response_class=HTMLResponse)
async def alertas_page(request: Request):
    return templates.TemplateResponse("alertas.html", {"request": request})

@app.get("/empresas", response_class=HTMLResponse)
async def empresas_page(request: Request):
    return templates.TemplateResponse("empresas.html", {"request": request})

@app.get("/consultores", response_class=HTMLResponse)
async def consultores_page(request: Request):
    return templates.TemplateResponse("consultores.html", {"request": request})

@app.get("/prospeccao", response_class=HTMLResponse)
async def prospeccao(request: Request):
    return templates.TemplateResponse("prospeccao.html", {"request": request})

@app.get("/cronograma", response_class=HTMLResponse)
async def cronograma_page(request: Request):
    return templates.TemplateResponse("cronograma.html", {"request": request})

@app.get("/contratos", response_class=HTMLResponse)
async def contratos_page(request: Request):
    return templates.TemplateResponse("contratos.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/importacao", response_class=HTMLResponse)
async def importacao_page(request: Request):
    return templates.TemplateResponse("importacao.html", {"request": request})

@app.get("/usuarios", response_class=HTMLResponse)
async def usuarios_page(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

@app.get("/relatorios", response_class=HTMLResponse)
async def relatorios_page(request: Request):
    return templates.TemplateResponse("relatorios.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Sistema de relacionamento com a industria 1.03 rodando"}
