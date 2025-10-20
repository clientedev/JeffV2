from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class FuncaoUsuario(str, enum.Enum):
    ADMIN = "Admin"
    CONSULTOR = "Consultor"
    FINANCEIRO = "Financeiro"
    VISUALIZADOR = "Visualizador"

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
    sigla = Column(String(50))
    porte = Column(String(50))
    er = Column(String(100))
    carteira = Column(String(100))
    endereco = Column(String(500))
    bairro = Column(String(100))
    zona = Column(String(50))
    municipio = Column(String(100))
    estado = Column(String(2))
    pais = Column(String(100))
    area = Column(String(255))
    cnae_principal = Column(String(50))
    descricao_cnae = Column(Text)
    tipo_empresa = Column(String(100))
    cadastro_atualizacao = Column(DateTime)
    num_funcionarios = Column(Integer)
    observacao = Column(Text)
    segmento = Column(String(255))
    regiao = Column(String(100))
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    propostas = relationship("Proposta", back_populates="empresa")

class Consultor(Base):
    __tablename__ = "consultores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    nif = Column(String(50), unique=True, index=True)
    cargo = Column(String(100))
    ativo = Column(Boolean, default=True)
    dados_iniciais = Column(Boolean, default=False)
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

class AlocacaoCronograma(Base):
    __tablename__ = "alocacoes_cronograma"
    
    id = Column(Integer, primary_key=True, index=True)
    consultor_id = Column(Integer, ForeignKey("consultores.id"), nullable=False)
    data = Column(Date, nullable=False, index=True)
    periodo = Column(String(10), nullable=False)  # M (Manhã) ou T (Tarde)
    codigo_projeto = Column(String(100))  # Ex: C-PRODMEC, K-KAMAPRI2
    nif = Column(String(50))  # Número de identificação do consultor
    observacao = Column(Text)
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    consultor = relationship("Consultor", foreign_keys=[consultor_id])

class Contato(Base):
    __tablename__ = "contatos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(255), index=True)
    cnpj = Column(String(18), index=True)
    carteira = Column(String(100))
    porte = Column(String(50))
    er = Column(String(100))
    contato = Column(String(255))
    ponto_focal = Column(String(255))
    cargo = Column(String(100))
    proprietario_socio = Column(String(255))
    telefone_fixo = Column(String(20))
    celular = Column(String(20))
    celular2 = Column(String(20))
    email = Column(String(255))
    emails_voltaram = Column(String(255))
    observacoes = Column(Text)
    atualizacao = Column(Date)
    dados_iniciais = Column(Boolean, default=False)  # Marca se é dado inicial fixo
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LinhaTecnologia(Base):
    __tablename__ = "linha_tecnologia"
    
    id = Column(Integer, primary_key=True, index=True)
    linha = Column(String(100))
    tipo_programa = Column(String(100))
    cnpj = Column(String(18), index=True)
    empresa = Column(String(255), index=True)
    porte = Column(String(50))
    er = Column(String(100))
    sigla = Column(String(50))
    t3 = Column(String(100))
    status_etapa = Column(String(100))
    oportunidade = Column(String(100))
    numero_proposta = Column(String(50), index=True)
    ordem_venda = Column(String(50))
    emissor_proposta = Column(String(255))
    cfp_parceiro = Column(String(100))
    solucao = Column(Text)
    ch = Column(String(50))
    consultor = Column(String(255))
    dados_socios_informados = Column(String(50))
    contrato_enviado_empresa = Column(String(50))
    contrato_assinado_empresa = Column(String(50))
    data_contrato_assinado_senai = Column(Date)
    data_cadastro_sgt = Column(Date)
    data_upload_sgt = Column(Date)
    data_aceite_sgt = Column(Date)
    data_envio_relatorio_t1 = Column(Date)
    data_cobranca_empresa = Column(Date)
    cadastro_plataforma_ok = Column(String(50))
    data_cobranca_sebrae = Column(Date)
    contrato_sebrae_enviado = Column(String(50))
    data_resposta_sebrae = Column(Date)
    requisicao_grm = Column(String(100))
    data_inicio = Column(Date)
    data_termino = Column(Date)
    reuniao_kickoff_confirmada = Column(String(50))
    reuniao_final_agendada = Column(String(50))
    presencial = Column(String(50))
    gratuidade = Column(String(50))
    valor_proposta = Column(Numeric(12, 2))
    situacao = Column(String(100))
    numero_demanda = Column(String(100))
    codigo_rae = Column(String(100))
    mov_1_1_57 = Column(String(50))
    relatorio_priorizacao_enviado = Column(String(50))
    relatorio_smart_factory = Column(String(50))
    relatorio_final_enviado = Column(String(50))
    relatorio_educacional_enviado = Column(String(50))
    data_conclusao_sgt = Column(Date)
    envio_auditoria = Column(String(50))
    retorno_auditoria = Column(String(50))
    data_prestacao_contas = Column(Date)
    data_pesquisa_satisfacao = Column(Date)
    observacoes = Column(Text)
    especifico_saldo = Column(String(255))
    passou_ali_2023 = Column(String(50))
    ali_2024_convidar = Column(String(50))
    t3_solucao_1_2024 = Column(Text)
    t3_solucao_2_2024 = Column(Text)
    aceitou = Column(String(50))
    qual_3_etapa = Column(Text)
    t4_proposto_2024 = Column(Text)
    aceitou_2 = Column(String(50))
    follow_2024 = Column(String(255))
    continuidade = Column(String(255))
    etapa_5_ou_6 = Column(String(255))
    fez_efici_energ = Column(String(50))
    obs2 = Column(Text)
    ano = Column(Integer)
    mes = Column(String(20))
    inu = Column(String(50))
    hubspot = Column(String(50))
    nova_proposta = Column(String(50))
    valor_sap = Column(Numeric(12, 2))
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LinhaEducacional(Base):
    __tablename__ = "linha_educacional"
    
    id = Column(Integer, primary_key=True, index=True)
    linha = Column(String(100))
    cliente = Column(String(255))
    cnpj = Column(String(18), index=True)
    estabelecimento = Column(String(255), index=True)
    numero_cotacao = Column(String(50))
    data_envio_cotacao = Column(Date)
    data_follow = Column(Date)
    status_cotacao = Column(String(100))
    motivo = Column(String(255))
    programa = Column(String(255))
    tipo = Column(String(100))
    cfp_proposta = Column(String(100))
    cfp_parceiro = Column(String(100))
    modalidade = Column(String(100))
    ch = Column(String(50))
    turno = Column(String(50))
    data_inicio = Column(Date)
    data_termino = Column(Date)
    numero_proposta = Column(String(50), index=True)
    numero_ordem_venda = Column(String(50))
    valor = Column(Numeric(12, 2))
    situacao = Column(String(100))
    status_proposta = Column(String(100))
    receita_espelhada = Column(Numeric(12, 2))
    solicitacao_mdi = Column(Date)
    follow_mdi = Column(Date)
    recebimento_mdi = Column(Date)
    turma = Column(String(100))
    instrutor_1 = Column(String(255))
    ch_c1 = Column(String(50))
    instrutor_2 = Column(String(255))
    ch_c2 = Column(String(50))
    status_servico = Column(String(100))
    emissao_certificados = Column(Date)
    assinatura_certificados = Column(Date)
    data_entrega_certificados = Column(Date)
    pesquisa_satisfacao = Column(String(10))
    codigo_material = Column(String(100))
    quantidade_estoque_atual = Column(Integer)
    observacoes = Column(Text)
    ano = Column(Integer)
    mes = Column(String(20))
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prospeccao(Base):
    __tablename__ = "prospeccao"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(255), nullable=False, index=True)
    cnpj = Column(String(18), index=True)
    porte = Column(String(50))
    er = Column(String(100))
    contato = Column(String(255))
    cargo = Column(String(100))
    email = Column(String(255))
    celular = Column(String(20))
    telefone = Column(String(20))
    tipo_programa = Column(String(100))
    status = Column(String(50), default='Novo')  # Novo, Em andamento, Concluído, Perdido
    responsavel = Column(String(255))
    data_ligacao = Column(Date)
    oportunidade = Column(String(500))
    observacoes = Column(Text)
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    followups = relationship("FollowUp", back_populates="prospeccao", cascade="all, delete-orphan")

class FollowUp(Base):
    __tablename__ = "followups"
    
    id = Column(Integer, primary_key=True, index=True)
    prospeccao_id = Column(Integer, ForeignKey("prospeccao.id"), nullable=False, index=True)
    data = Column(DateTime, nullable=False, default=datetime.utcnow)
    responsavel = Column(String(255))
    tipo = Column(String(50))  # Ligação, Email, Reunião, WhatsApp
    descricao = Column(Text)
    proximo_contato = Column(Date)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    prospeccao = relationship("Prospeccao", back_populates="followups")

class CarteiraGRM(Base):
    __tablename__ = "carteira_grm"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), index=True)
    empresa = Column(String(255), index=True)
    porte = Column(String(50))
    proposta = Column(String(50))
    solucao = Column(String(500))
    consultor = Column(String(255))
    data_inicio = Column(Date)
    data_termino = Column(Date)
    ch = Column(String(50))
    valor = Column(Numeric(12, 2))
    status = Column(String(100))
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PesquisaSatisfacao(Base):
    __tablename__ = "pesquisas_satisfacao"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), index=True)
    empresa = Column(String(255), index=True)
    numero_proposta = Column(String(50))
    data_resposta = Column(Date)
    nota_geral = Column(Numeric(3, 1))
    nota_consultoria = Column(Numeric(3, 1))
    nota_consultor = Column(Numeric(3, 1))
    recomendaria = Column(String(10))  # Sim, Não
    comentarios = Column(Text)
    dados_iniciais = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Solucao(Base):
    __tablename__ = "solucoes"
    
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String(255))
    subgrupo = Column(String(255))
    titulo = Column(String(500), nullable=False)
    etapa = Column(String(100))
    horas_me = Column(Integer)
    horas_epp = Column(Integer)
    estrategia = Column(String(50))  # Presencial, Remoto, Híbrido
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
