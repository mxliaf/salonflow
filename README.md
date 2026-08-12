# SalonFlow — Sistema de Agendamento de Horários de Salão de Beleza

O **SalonFlow** é um sistema completo e moderno para agendamento de serviços em salões de beleza, permitindo que clientes visualizem horários disponíveis em tempo real e realizem reservas sem conflitos. Administradores e funcionários possuem um painel exclusivo atualizado em tempo real via WebSockets.

---

## 🛠️ Tecnologias Utilizadas

### **Landing Page** (`landing/`)
- **Astro 5** + **Tailwind CSS** + **TypeScript**
- Performance máxima com SSG (Static Site Generation)
- Tipografia premium: Outfit + Plus Jakarta Sans

### **Frontend** (`frontend/`)
- **Next.js (App Router)** & **React 18**
- **Estilização**: TailwindCSS + Lucide Icons + Design Responsivo
- **Consumo da API**: Fetch nativo tipado com `NEXT_PUBLIC_API_URL` e `NEXT_PUBLIC_WS_URL`

### **Backend** (`backend/`)
- **Python 3.12+** & **FastAPI**
- **ORM & Banco de Dados**: SQLAlchemy 2.0 (modo assíncrono), Pydantic v2 para schemas
- **Suporte de BD**: PostgreSQL (`asyncpg`) e SQLite (`aiosqlite` para dev local rápido)
- **Autenticação**: JWT (`python-jose`) + Hashing de senha com `passlib[bcrypt]`
- **Real-Time**: WebSockets para notificação instantânea no painel do salão

---

## 📁 Estrutura do Projeto

```text
salonflow/
├── landing/                   # Astro — Landing Page institucional
│   ├── src/
│   │   ├── components/        # Navbar, Hero, Services, Prices, Testimonials, CTA, Footer
│   │   ├── layouts/           # Layout.astro (base HTML)
│   │   ├── pages/             # index.astro (ponto de entrada)
│   │   └── styles/            # global.css (Tailwind directives)
│   ├── astro.config.mjs
│   ├── tailwind.config.mjs
│   ├── .env.example
│   └── package.json
├── frontend/                  # Next.js — Dashboard de Agendamento
│   ├── src/
│   │   ├── app/               # Estrutura do Next.js App Router
│   │   ├── components/        # Componentes reutilizáveis (Navbar, Footer)
│   │   └── lib/               # API fetch client e AuthContext
│   ├── .env.example
│   └── package.json
├── backend/                   # FastAPI — API REST + WebSocket
│   ├── app/
│   │   ├── api/v1/endpoints/  # Rotas e Endpoints (auth, servicos, agendamentos, websocket)
│   │   ├── core/              # Configurações, segurança JWT
│   │   ├── crud/              # Camada de acesso ao banco (CRUD classes)
│   │   ├── db/                # Conexão e sessão do banco de dados
│   │   ├── models/            # Modelos SQLAlchemy (Usuario, Servico, Agendamento)
│   │   ├── schemas/           # Schemas Pydantic v2 de entrada e saída
│   │   └── services/          # Lógica de negócio (slots, conflitos, WebSocket)
│   ├── tests/                 # Suíte de testes automatizados (pytest)
│   ├── main.py                # Ponto de entrada
│   ├── requirements.txt
│   ├── .env.example
│   └── pyproject.toml
└── README.md
```

---

## 🚀 Como Executar Localmente

### **1. Landing Page (Astro)**

```bash
cd landing
cp .env.example .env
npm install
npm run dev
```

A landing estará disponível em `http://localhost:4321`.

---

### **2. Frontend (Next.js)**

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

O frontend estará acessível em `http://localhost:3000`.

---

### **3. Backend (FastAPI)**

```bash
cd backend
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

A API estará rodando em `http://localhost:8000`.
Documentação Swagger interativa em `http://localhost:8000/docs`.

#### Executar os Testes Automatizados (Pytest):
```bash
uv run pytest -v
```

---

## 🔐 Credenciais Padrão (Semeadas Automaticamente)

Ao iniciar o backend pela primeira vez, as seguintes contas de teste são geradas automaticamente:

- **Administrador**: `admin@salonflow.com` | Senha: `admin123`
- **Funcionário**: `funcionario@salonflow.com` | Senha: `func123`
