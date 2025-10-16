from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class FuncaoUsuario(str, enum.Enum):
    ADMIN = "Admin"
    GESTOR = "Gestor"
    CONSULTOR = "Consultor"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    funcao = Column(String(50), nullable=False)  # Admin, Consultor, Financeiro
    consultor_id = Column(Integer, ForeignKey("consultores.id"), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    consultor = relationship("Consultor", foreign_keys=[consultor_id])

class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    segmento = Column(String(255))
    regiao = Column(String(100))
    er = Column(String(100))
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    propostas = relationship("Proposta", back_populates="empresa")

class Consultor(Base):
    __tablename__ = "consultores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    cargo = Column(String(100))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    propostas = relationship("Proposta", back_populates="consultor")

class Proposta(Base):
    __tablename__ = "propostas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_proposta = Column(String(50), unique=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    consultor_id = Column(Integer, ForeignKey("consultores.id"))
    solucao = Column(String(255))
    data_contato = Column(Date)
    data_proposta = Column(Date)
    valor_proposta = Column(Numeric(12, 2))
    data_fechamento = Column(Date)
    status = Column(String(50))  # Em andamento, Fechado, Perdido
    resultado = Column(String(100))
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="propostas")
    consultor = relationship("Consultor", back_populates="propostas")
    cronogramas = relationship("Cronograma", back_populates="proposta")
    contratos = relationship("Contrato", back_populates="proposta")

class Cronograma(Base):
    __tablename__ = "cronogramas"
    
    id = Column(Integer, primary_key=True, index=True)
    proposta_id = Column(Integer, ForeignKey("propostas.id"), nullable=False)
    data_inicio = Column(Date)
    data_termino = Column(Date)
    horas_previstas = Column(Numeric(8, 2))
    horas_executadas = Column(Numeric(8, 2), default=0)
    percentual_conclusao = Column(Numeric(5, 2), default=0)
    status = Column(String(50))  # Não iniciado, Em andamento, Concluído, Atrasado
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    proposta = relationship("Proposta", back_populates="cronogramas")
    tarefas = relationship("Tarefa", back_populates="cronograma")

class Tarefa(Base):
    __tablename__ = "tarefas"
    
    id = Column(Integer, primary_key=True, index=True)
    cronograma_id = Column(Integer, ForeignKey("cronogramas.id"), nullable=False)
    descricao = Column(String(500), nullable=False)
    data_vencimento = Column(Date)
    concluida = Column(Boolean, default=False)
    ordem = Column(Integer)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cronograma = relationship("Cronograma", back_populates="tarefas")

class Contrato(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, index=True)
    proposta_id = Column(Integer, ForeignKey("propostas.id"), nullable=False)
    numero_contrato = Column(String(50), unique=True, index=True)
    data_assinatura = Column(Date)
    data_vencimento = Column(Date)
    valor = Column(Numeric(12, 2))
    status_pagamento = Column(String(50))  # Pendente, Pago, Vencido, Cancelado
    observacao = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    proposta = relationship("Proposta", back_populates="contratos")

class Feriado(Base):
    __tablename__ = "feriados"
    
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, unique=True, nullable=False, index=True)
    descricao = Column(String(255))
    tipo = Column(String(50))  # Nacional, Estadual, Municipal
