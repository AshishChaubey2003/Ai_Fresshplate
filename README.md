# 🍽️ AI FreshPlate — AI-Powered Food Ordering & Food Rescue Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-green?style=flat-square&logo=django)
![DRF](https://img.shields.io/badge/DRF-REST_API-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square&logo=postgresql)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-AI-orange?style=flat-square&logo=google)
![JWT](https://img.shields.io/badge/JWT-Auth-yellow?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![Live](https://img.shields.io/badge/Live-Deployed-brightgreen?style=flat-square)

> A full-stack food ordering and food rescue platform built with Django REST Framework and Google Gemini AI — featuring smart food recommendations, 3-tier role-based access, cart management, and a food donation lifecycle module.

🌐 **Live Demo:** [ai-fresshplate.vercel.app](https://ai-fresshplate.vercel.app/) &nbsp;|&nbsp; 🔗 **Backend API:** [Render](https://render.com)

---

## 📌 What This Project Does

**AI FreshPlate** solves two real problems:
1. **Food Ordering** — Customers browse, cart, and order food with real-time tracking
2. **Food Rescue** — Donors list surplus food, rescue centers claim it via a 3-step approval lifecycle

Backed by **Google Gemini AI** for personalized food recommendations and a **CI/CD pipeline** that auto-deploys on every Git push.

---

## ✨ Key Features & Numbers

- 🔐 **JWT Authentication** — Access + refresh token flow, secure login & registration
- 👥 **3-Tier RBAC** — Admin, Customer, Donor with strict permission classes per endpoint
- 🛒 **Dynamic Cart** — Add, update, remove items; 5+ order status transitions with real-time tracking
- 🍱 **Food Management** — Browse and manage food items and categories
- 🤝 **Food Rescue Module** — 3-step donor → rescue center approval lifecycle
- 🤖 **Gemini AI Chatbot** — Personalized food recommendations via Google Gemini API
- 📡 **10+ REST APIs** — Clean, scalable DRF endpoints with Swagger docs
- 🗄️ **PostgreSQL** — Optimized ORM queries with custom permission classes
- 🚀 **CI/CD** — Auto-deploy on every Git push via Render + Vercel

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.x, Django REST Framework |
| Authentication | JWT (SimpleJWT) |
| Database | PostgreSQL + Django ORM |
| AI Assistant | Google Gemini API |
| Frontend | React, JavaScript, HTML5, CSS3, Axios |
| Deployment | Render (backend), Vercel (frontend) |
| DevOps | Docker, CI/CD (GitHub → Render) |

---

## 📁 Project Structure

```
Ai_Fresshplate/
├── backend/
│   ├── chatbot/             # Google Gemini AI chatbot integration
│   ├── donations/           # Food rescue & donation module
│   ├── food/                # Food items & categories
│   ├── freshplate/          # Django project settings
│   ├── media/               # Uploaded media files
│   ├── orders/              # Order placement & tracking
│   ├── users/               # Auth, roles & profiles
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   └── (React + JS + HTML/CSS)
├── docker-compose.yml
└── .env.example
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Node.js (for frontend)
- Docker (optional)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AshishChaubey2003/Ai_Fresshplate.git
cd Ai_Fresshplate/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

---

## 🔑 Environment Variables

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

DB_NAME=freshplate_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

GEMINI_API_KEY=your_google_gemini_api_key
```

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login & get JWT token |
| GET | `/api/food/` | List all food items |
| POST | `/api/cart/` | Add item to cart |
| POST | `/api/orders/` | Place an order |
| GET | `/api/orders/` | List & track orders |
| GET | `/api/donations/` | List food donations |
| POST | `/api/donations/claim/` | Rescue center claims donation |
| POST | `/api/chatbot/` | Chat with Gemini AI assistant |
| GET | `/api/admin/dashboard/` | Admin overview (Admin only) |

---

## 👥 User Roles & Permissions

| Role | Permissions |
|------|------------|
| **Admin** | Full access — manage users, food, orders, donations |
| **Customer** | Browse food, manage cart, place & track orders, use chatbot |
| **Donor** | List food donations, manage 3-step rescue lifecycle |

---

## 🤖 AI Chatbot

FreshPlate integrates **Google Gemini AI** to power an intelligent assistant that helps users:

- 🔍 Discover and search menu items
- 💡 Get personalized food recommendations
- ❓ Answer FAQs about orders and delivery
- 🍕 Suggest meals based on preferences and dietary needs

---

## 🚀 Roadmap

- [ ] Add Stripe payment integration
- [ ] Push notifications for order status
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard for Admin

---

## 📄 License

MIT License — open source and free to use.

---

<p align="center">Built by <a href="https://github.com/AshishChaubey2003">Ashish Kumar Chaubey</a> — B.Tech CSE 2025 | Lucknow, India</p>
<p align="center">
  <a href="https://www.linkedin.com/in/ashishchaubey2dec/">LinkedIn</a> •
  <a href="https://personal-portfolio-website-one-azure.vercel.app/">Portfolio</a> •
  <a href="mailto:sashishchaubey1234@gmail.com">Email</a>
</p>
