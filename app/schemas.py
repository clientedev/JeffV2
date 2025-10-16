from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    funcao: str
    consultor_id: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

class EmpresaBase(BaseModel):
    cnpj: str
    nome: str
    segmento: Optional[str] = None
    regiao: Optional[str] = None
    er: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaResponse(EmpresaBase):
    id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class ConsultorBase(BaseModel):
    nome: str
    email: EmailStr
    cargo: Optional[str] = None

class ConsultorCreate(ConsultorBase):
    pass

class ConsultorResponse(ConsultorBase):
    id: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

class PropostaBase(BaseModel):
    numero_proposta: str
    empresa_id: int
    consultor_id: Optional[int] = None
    solucao: Optional[str] = None
    data_contato: Optional[date] = None
    data_proposta: Optional[date] = None
    valor_proposta: Optional[Decimal] = None
    data_fechamento: Optional[date] = None
    status: Optional[str] = "Em andamento"
    resultado: Optional[str] = None
    observacoes: Optional[str] = None

class PropostaCreate(PropostaBase):
    pass

class PropostaUpdate(BaseModel):
    numero_proposta: Optional[str] = None
    empresa_id: Optional[int] = None
    consultor_id: Optional[int] = None
    solucao: Optional[str] = None
    data_contato: Optional[date] = None
    data_proposta: Optional[date] = None
    valor_proposta: Optional[Decimal] = None
    data_fechamento: Optional[date] = None
    status: Optional[str] = None
    resultado: Optional[str] = None
    observacoes: Optional[str] = None

class PropostaResponse(PropostaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

class CronogramaBase(BaseModel):
    proposta_id: int
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    horas_previstas: Optional[Decimal] = None
    horas_executadas: Optional[Decimal] = Field(default=Decimal("0"))
    percentual_conclusao: Optional[Decimal] = Field(default=Decimal("0"))
    status: Optional[str] = "Não iniciado"
    observacoes: Optional[str] = None

class CronogramaCreate(CronogramaBase):
    pass

class CronogramaUpdate(BaseModel):
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    horas_previstas: Optional[Decimal] = None
    horas_executadas: Optional[Decimal] = None
    percentual_conclusao: Optional[Decimal] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class CronogramaResponse(CronogramaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

class TarefaBase(BaseModel):
    cronograma_id: int
    descricao: str
    data_vencimento: Optional[date] = None
    concluida: bool = False
    ordem: Optional[int] = None

class TarefaCreate(TarefaBase):
    pass

class TarefaResponse(TarefaBase):
    id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

class ContratoBase(BaseModel):
    proposta_id: int
    numero_contrato: str
    data_assinatura: Optional[date] = None
    data_vencimento: Optional[date] = None
    valor: Optional[Decimal] = None
    status_pagamento: Optional[str] = "Pendente"
    observacao: Optional[str] = None

class ContratoCreate(ContratoBase):
    pass

class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    data_assinatura: Optional[date] = None
    data_vencimento: Optional[date] = None
    valor: Optional[Decimal] = None
    status_pagamento: Optional[str] = None
    observacao: Optional[str] = None

class ContratoResponse(ContratoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

class FeriadoBase(BaseModel):
    data: date
    descricao: Optional[str] = None
    tipo: Optional[str] = None

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoResponse(FeriadoBase):
    id: int
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ImportacaoResponse(BaseModel):
    sucesso: bool
    registros_importados: int
    erros: list = []
