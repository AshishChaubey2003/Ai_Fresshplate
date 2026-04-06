# 🍽️ FreshPlate — AI-Powered Food Ordering System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-green?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/Django_REST_Framework-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?style=for-the-badge&logo=postgresql)
![Claude AI](https://img.shields.io/badge/Claude_AI-Anthropic-orange?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-yellow?style=for-the-badge)

> A full-stack food ordering web application powered by Django REST Framework and Claude AI — featuring smart food recommendations, role-based access, cart management, and a food donation module.

---

## 📌 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Overview](#api-overview)
- [User Roles](#user-roles)
- [AI Chatbot](#ai-chatbot)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 About the Project

**FreshPlate** is a modern food ordering platform that combines the power of Django REST Framework with Anthropic's Claude AI to deliver a seamless and intelligent food ordering experience. Users can browse menus, place orders, donate food, and interact with an AI chatbot — all through a clean HTML/CSS/JS frontend consuming a robust REST API backend.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure login & registration with token-based auth
- 👥 **3 User Roles** — Admin, Customer, and Donor with role-based permissions
- 🛒 **Cart System** — Add, update, remove items and place orders
- 🍱 **Food Management** — Browse and manage food items and categories
- 📦 **Order Management** — Place and track food orders in real time
- 🤝 **Food Donation Module** — Donors can list and manage food donations
- 🤖 **AI Chatbot** — Claude AI-powered assistant for menu help & recommendations
- 🌐 **REST API** — Clean, scalable API endpoints for all features
- 🗄️ **PostgreSQL** — Reliable relational database for all data storage

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.x, Django REST Framework |
| Authentication | JWT (SimpleJWT) |
| Database | PostgreSQL |
| AI Assistant | Anthropic Claude API |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure

```
FreshPlate/
├── freshplate/          # Main Django project settings
├── users/               # User auth, roles & profiles
├── food/                # Food items & categories
├── orders/              # Order placement & tracking
├── donations/           # Food donation module
├── chatbot/             # Claude AI chatbot integration
├── frontend/            # HTML, CSS, JS files
├── .env                 # Environment variables (not committed)
├── .gitignore
├── manage.py
└── requirements.txt


FreshPlate/
├── backend/
│   ├── chatbot/             # Claude AI chatbot integration
│   ├── donations/           # Food donation module
│   ├── food/                # Food items & categories
│   ├── freshplate/          # Main Django project settings
│   ├── media/               # Uploaded media files
│   ├── orders/              # Order placement & tracking
│   ├── users/               # User auth, roles & profiles
│   ├── .env                 # Environment variables (not committed)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   └── (HTML, CSS, JS files)
└── freshplate_env/          # Virtual environment (not committed)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AshishChaubey2003/Ai_Fresshplate.git
cd Ai_Fresshplate

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

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

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_django_secret_key

DEBUG=True

DB_NAME=freshplate_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

ANTHROPIC_API_KEY=your_anthropic_api_key
```

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login & get JWT token |
| GET | `/api/food/` | List all food items |
| POST | `/api/orders/` | Place an order |
| GET | `/api/orders/` | List user orders |
| POST | `/api/cart/` | Add item to cart |
| GET | `/api/donations/` | List food donations |
| POST | `/api/chatbot/` | Chat with AI assistant |

---

## 👥 User Roles

| Role | Permissions |
|------|------------|
| **Admin** | Full access — manage users, food, orders, donations |
| **Customer** | Browse food, manage cart, place orders, use chatbot |
| **Donor** | List and manage food donations |

---

## 🤖 AI Chatbot

FreshPlate integrates **Anthropic's Claude AI** to power an intelligent chatbot that helps users:

- 🔍 Discover menu items
- 💡 Get personalized food recommendations
- ❓ Answer FAQs about orders and delivery
- 🍕 Suggest meals based on preferences

The chatbot is accessible via the `/api/chatbot/` endpoint and is integrated into the frontend for a seamless chat experience.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

```bash
git checkout -b feature/your-feature-name
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ by <a href="https://github.com/AshishChaubey2003">Ashish Chaubey</a></p>
