# 🚀 Suvan – AI-Powered MSME & CA Opportunity Platform

> An AI-powered platform that empowers **Micro, Small & Medium Enterprises (MSMEs)** and **Chartered Accountants (CAs)** by simplifying access to government schemes, subsidies, grants, tenders, compliance guidance, and business opportunities through intelligent AI assistance.

---

# 📖 Overview

Suvan is a unified AI-powered platform built to bridge the gap between government opportunities, MSMEs, and Chartered Accountants.

Business owners often struggle to discover relevant schemes, grants, subsidies, tenders, and financial support because information is spread across multiple government portals. Similarly, Chartered Accountants spend significant time researching regulations, identifying client opportunities, and simplifying compliance requirements.

Suvan centralizes these services into a single platform where users can discover opportunities, understand eligibility, receive AI-assisted guidance, and access business insights through an intuitive and responsive interface.

The platform combines a modern React frontend with a scalable FastAPI backend and an AI orchestration layer to provide intelligent, context-aware assistance while ensuring deterministic business logic for eligibility-related decisions.

---

# 🎯 Key Features

## 👨‍💼 For MSMEs

- 🔍 Government Scheme Discovery
- 💰 Subsidy & Grant Recommendations
- 🏦 Loan & Funding Opportunities
- 📋 Tender Discovery
- 🤖 AI Business Assistant
- 📈 Personalized Dashboard
- 📑 Eligibility Guidance

---

## 👨‍💼 For Chartered Accountants

- 📁 Client Portfolio Management
- 📊 Opportunity Discovery for Clients
- 🧾 Compliance Assistance
- 🤖 AI Tax & Business Guidance
- 📑 Scheme Matching
- 📈 Advisory Support

---

## 🤖 AI Capabilities

- AI Chat Assistant
- Intelligent Opportunity Search
- AI-powered Explanations
- Context-aware Responses
- Summarization & Drafting
- Document Understanding (Architecture Ready)
- Model Routing & AI Orchestration

> **Note:** AI assists with explanations, drafting, and summarization. All eligibility-related decisions remain deterministic and rule-based.

---

# 🛠️ Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router
- Framer Motion
- Firebase Authentication
- Google OAuth

---

## Backend

- FastAPI
- Python
- SQLAlchemy (Async)
- PostgreSQL
- Alembic
- Docker
- Docker Compose

---

## AI

- Fireworks AI
- Gemma Models
- Qwen Models
- AI Orchestrator
- Prompt Manager
- Context Builder
- Model Registry

---

## Deployment

- Vercel
- Docker
- PostgreSQL

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/divyammanas/AMD-AI-Powered-MSME-WebApp.git

cd AMD-AI-Powered-MSME-WebApp
```

---

# 💻 Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

# ⚙️ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment.

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000
```

Health Check:

```
http://127.0.0.1:8000/api/v1/health
```

---

# 🗄️ Database Configuration

Create a `.env` file inside the backend directory.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/suvan

FIREWORKS_API_KEY=your_fireworks_api_key

FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1

FIREWORKS_MODEL=accounts/fireworks/models/gemma-4-31b-it
```

Run migrations:

```bash
alembic upgrade head
```

---

# 🐳 Docker Setup

Start PostgreSQL and backend services:

```bash
docker compose up -d
```

Run migrations:

```bash
alembic upgrade head
```

If Docker is unavailable, you can use a hosted PostgreSQL database (Neon, Railway, Supabase, etc.) by updating the `DATABASE_URL` in your `.env` file.

---

# 🤖 AI Architecture

The backend uses an AI orchestration layer that separates business logic from AI providers, allowing the platform to scale and support multiple models.

Current capabilities include:

| Capability | Model |
|------------|-------|
| AI Chat | Gemma 4 |
| Reasoning | Gemma 4 |
| Opportunity Explanation | Gemma 4 |
| Document Understanding | Qwen |
| Embeddings | Qwen Embedding |
| Reranking | Qwen Reranker |

The architecture is designed so that future AI providers and models can be integrated without modifying the core business services.

---

# 🔐 Authentication

- Firebase Authentication
- Google OAuth
- Secure User Sessions

---

# 📡 API

Base URL

```
/api/v1
```

### Health Endpoint

```
GET /health
```

### Client Management

```
POST   /clients
GET    /clients
GET    /clients/{id}
PATCH  /clients/{id}
DELETE /clients/{id}
```

The backend is structured to support additional APIs for AI chat, opportunity discovery, user management, recommendations, and future business services.

---

# 🌍 Future Scope

- AI Opportunity Agent
- OCR-based Document Processing
- Automated Scheme Recommendation Engine
- Multilingual Support
- Personalized Notifications
- Application Tracking
- Advanced Business Analytics
- Dedicated CA Workspace
- Enhanced MSME Dashboard

---

# 👥 Contributors

### Divyam Manas

- Frontend Development
- UI/UX Design
- Responsive Design
- Deployment

### Abhay Prakash
- Backend Development
- Agentic Development
- product Designer

### Atharv Mishra
- Product Manager
- strategy
- Product Designer

### Suvan

- Backend Development
- FastAPI APIs
- PostgreSQL Integration
- SQLAlchemy
- Docker Configuration
- AI Orchestration
- Fireworks AI Integration

---

