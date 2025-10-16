# Sistema de Gestão Operacional

## Overview

This is a comprehensive operational, commercial, and administrative management system built with FastAPI and PostgreSQL. The system unifies business data from spreadsheets into a centralized platform for managing prospecting, schedules, contracts, and business intelligence dashboards. It serves consulting firms that need to track client proposals, project timelines, consultant workloads, and financial contracts with automated alerts and reporting capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework**: FastAPI (Python)
- **Rationale**: FastAPI provides high performance, automatic API documentation, type safety with Pydantic, and built-in async support
- **Authentication**: JWT-based authentication using `python-jose` with bcrypt password hashing
- **Session Management**: OAuth2 password bearer tokens with 480-minute expiration

**Database ORM**: SQLAlchemy
- **Rationale**: Mature ORM with excellent PostgreSQL support, connection pooling, and declarative model definitions
- **Connection Pool**: Pre-configured with pool size of 10, max overflow of 20, and 300-second recycle time for production reliability

**Role-Based Access Control**: Three-tier permission system
- Admin: Full system access
- Consultor (Consultant): Limited to assigned proposals and projects
- Financeiro (Financial): Access to contracts and financial reporting
- Implementation uses function decorators and database-linked user roles

### Frontend Architecture

**Template Engine**: Jinja2 templates with server-side rendering
- **Rationale**: Simplifies development while maintaining security, reduces client-side complexity
- **Design System**: Custom CSS with dark theme using CSS variables for consistency
- **Component Structure**: Base template with block inheritance for consistent layout

**Visualization**: Plotly.js for interactive BI dashboards
- **Rationale**: Rich charting capabilities with responsive design and dark theme support

**Client Communication**: Vanilla JavaScript with Fetch API
- **Rationale**: No framework overhead, direct control over API interactions
- **Authentication**: Bearer token stored in localStorage, automatically included in request headers

### Data Models

**Core Entities**:
1. **Usuario** (User): System users with role-based permissions
2. **Empresa** (Company): Client companies with CNPJ identification
3. **Consultor** (Consultant): Project consultants linked to users
4. **Proposta** (Proposal): Sales proposals with conversion tracking
5. **Cronograma** (Schedule): Project timelines with progress tracking
6. **Contrato** (Contract): Financial contracts with payment tracking
7. **Feriado** (Holiday): Calendar management for scheduling

**Relationships**:
- One-to-Many: Empresa → Propostas, Proposta → Cronogramas, Proposta → Contratos
- User-Consultant linking for role-based data filtering
- Audit trails with creation timestamps on all entities

### API Structure

**RESTful Endpoints** organized by domain:
- `/api/login` - Authentication
- `/api/empresas` - Company CRUD
- `/api/consultores` - Consultant management
- `/api/propostas` - Proposal tracking with filters
- `/api/cronogramas` - Schedule management with progress calculation
- `/api/contratos` - Contract and payment tracking
- `/api/bi` - Business intelligence aggregations
- `/api/importacao` - Excel/CSV data import
- `/api/chatbot` - Natural language query interface
- `/api/relatorios` - PDF/Excel report generation
- `/api/alertas` - Automated alert system

**Design Patterns**:
- Dependency injection for database sessions and authentication
- Response models with Pydantic schemas for type safety
- Consistent error handling with HTTP status codes

### Alert System

**Automated Monitoring**:
- Contract expiration alerts (7-day lookahead)
- Overdue contracts tracking
- Schedule deadline warnings
- Stalled proposals (30+ days without updates)
- Critical tasks identification (low completion % near deadline)

**Implementation**: Centralized `/api/alertas/todos` endpoint aggregates all alert types with database queries using date comparisons

### Import/Export System

**Data Import**: Pandas-based Excel/CSV processing
- **Supported Formats**: .xlsx, .xls, .csv
- **Validation**: CNPJ cleaning, date parsing, duplicate detection
- **Batch Processing**: Row-by-row with error collection and rollback support

**Report Generation**:
- **PDF Reports**: ReportLab with custom styling for proposals, contracts, schedules
- **Excel Export**: OpenPyXL with formatting (fonts, alignment, fills)
- **Streaming Responses**: Memory-efficient file downloads

### Chatbot Interface

**Natural Language Queries**: Pattern matching for common business questions
- Contract expiration queries
- Project status inquiries
- Financial summaries
- Implementation uses keyword detection with database aggregations

## External Dependencies

### Database
- **PostgreSQL**: Primary relational database
- **Connection**: Via DATABASE_URL environment variable
- **Features Used**: Date functions, aggregations, foreign key constraints

### Python Libraries
- **FastAPI**: Web framework and API routing
- **SQLAlchemy**: ORM and database abstraction
- **Pydantic**: Data validation and serialization
- **python-jose**: JWT token handling
- **bcrypt**: Password hashing
- **pandas**: Data import/export and Excel processing
- **openpyxl**: Excel file reading/writing
- **reportlab**: PDF generation
- **python-multipart**: File upload handling

### Frontend Libraries
- **Plotly.js 2.27.0**: Interactive charting and visualizations
- **Font Awesome 6.4.0**: Icon library

### Environment Configuration
- **SESSION_SECRET**: JWT signing key (defaults to insecure value, should be overridden)
- **DATABASE_URL**: PostgreSQL connection string (required)
- **ADMIN_EMAIL**: Default admin user email
- **ADMIN_PASSWORD**: Default admin password

### File Storage
- **Static Assets**: Served from `/app/static` directory
- **Upload Processing**: Temporary file handling in memory via BytesIO
- **Attached Assets**: Sample Excel files in `/attached_assets` for initial data import

## Current Database Status

### Imported Data (October 16, 2025)
Successfully imported from Excel spreadsheets:
- **249 Companies** (Empresas) - Client companies with CNPJ and contact information
- **19 Consultants** (Consultores) - Project consultants assigned to proposals
- **224 Proposals** (Propostas) - Sales proposals with status tracking and consultant assignments
- **224 Schedules** (Cronogramas) - Project timelines with automatic progress calculation

### System Readiness
All 9 core requirements are implemented and functional:
1. ✅ Role-based authentication (Admin, Consultor, Financeiro)
2. ✅ Intelligent prospecting with advanced filters and statistics
3. ✅ Automated schedule progress tracking based on task completion
4. ✅ Contract billing analytics and payment tracking
5. ✅ BI Dashboard with interactive Plotly charts
6. ✅ Centralized smart alerts (contracts, deadlines, stalled proposals)
7. ✅ Excel/PDF export with custom filters
8. ✅ Intelligent chatbot for natural language queries
9. ✅ Responsive UI with dark theme

### Access Credentials
- **Admin User**: admin@sistema.com / admin123
- **Database**: PostgreSQL (Replit-managed, configured via DATABASE_URL)