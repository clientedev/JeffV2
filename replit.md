# Sistema de relacionamento com a industria

## Overview

This is a comprehensive industrial relationship management system built with FastAPI and PostgreSQL. The system unifies business data from spreadsheets into a centralized platform for managing companies, consultants, prospecting, schedules, contracts, and business intelligence dashboards. It serves consulting firms by tracking client proposals, project timelines, consultant workloads, and financial contracts with automated alerts and reporting capabilities. The system now includes advanced prospecting with follow-ups, detailed consultant performance metrics, an improved internal assistant, and comprehensive analytical reports.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework**: FastAPI (Python) for high performance, automatic API documentation, type safety with Pydantic, and async support.
**Authentication**: JWT-based authentication using `python-jose` with bcrypt password hashing and OAuth2 password bearer tokens with 480-minute expiration.
**Database ORM**: SQLAlchemy with PostgreSQL, configured with a connection pool for reliability.
**Role-Based Access Control**: Three-tier permission system (Admin, Consultor, Financeiro, Visualizador) implemented with function decorators and database-linked user roles.

### Frontend Architecture

**Template Engine**: Jinja2 templates with server-side rendering for simplified development and security.
**Design System**: Custom CSS with a dark theme using CSS variables for consistency.
**Visualization**: Plotly.js for interactive BI dashboards with responsive design and dark theme support.
**Client Communication**: Vanilla JavaScript with Fetch API for direct API interactions, using bearer tokens stored in localStorage for authentication.

### Data Models

**Core Entities**: Usuario, Empresa, Consultor, Proposta, Cronograma, AlocacaoCronograma, Contrato, Feriado, Contato, LinhaTecnologia, LinhaEducacional.
**Relationships**: One-to-Many relationships exist between core entities (e.g., Empresa to Propostas). Consultant allocations are tracked daily. Initial data imported from Excel is marked `dados_iniciais=True` and protected from modification via API.

### API Structure

**RESTful Endpoints** are organized by domain, including `/api/login`, `/api/empresas`, `/api/consultores`, `/api/propostas`, `/api/cronogramas`, `/api/contratos`, `/api/contatos`, `/api/linha-tecnologia`, `/api/linha-educacional`, `/api/bi`, `/api/importacao`, `/api/chatbot`, `/api/relatorios`, and `/api/alertas`.
**Design Patterns**: Dependency injection for database sessions and authentication, Pydantic schemas for type safety, and consistent error handling.

### Alert System

**Automated Monitoring**: Includes alerts for contract expiration, overdue contracts, schedule deadline warnings, and stalled proposals. A centralized `/api/alertas/todos` endpoint aggregates all alert types.

### Import/Export System

**Data Import**: Pandas-based Excel/CSV processing supporting .xlsx, .xls, .csv formats with validation, duplicate detection, and batch processing. Seed data import is idempotent and marks initial data as protected.
**Report Generation**: PDF reports using ReportLab and Excel exports using OpenPyXL with custom formatting and streaming responses.

### Chatbot Interface

**Natural Language Queries**: Supports pattern matching for common business questions, such as contract expiration, project status, and financial summaries. It has optional OpenAI integration for enhanced intelligence, operating with predefined patterns if no API key is provided.

## External Dependencies

### Database
- **PostgreSQL**: Primary relational database, connected via `DATABASE_URL` environment variable.

### Python Libraries
- **FastAPI**: Web framework.
- **SQLAlchemy**: ORM.
- **Pydantic**: Data validation.
- **python-jose**: JWT handling.
- **bcrypt**: Password hashing.
- **pandas**: Data import/export.
- **openpyxl**: Excel handling.
- **reportlab**: PDF generation.
- **python-multipart**: File uploads.
- **OpenAI**: Optional integration for the chatbot.

### Frontend Libraries
- **Plotly.js 2.27.0**: Interactive charting.
- **Font Awesome 6.4.0**: Icon library.

### Environment Configuration
- **SESSION_SECRET**: JWT signing key.
- **DATABASE_URL**: PostgreSQL connection string.
- **ADMIN_EMAIL**: Default admin user email.
- **ADMIN_PASSWORD**: Default admin password.
- **OPENAI_API_KEY**: Optional API key for advanced chatbot features.