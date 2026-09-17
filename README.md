# 🍽️ FreshPlate — AI-Powered Food Ordering & Food Rescue Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/DRF-REST_API-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue?style=for-the-badge&logo=postgresql)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-orange?style=for-the-badge&logo=google)
![JWT](https://img.shields.io/badge/JWT-Auth-yellow?style=for-the-badge)

A cloud kitchen and food rescue platform. Customers order freshly cooked meals, donors
list surplus food for rescue centres to collect, and an AI assistant answers questions
using the **real menu and the user's real orders** instead of making things up.

🌐 **Live app:** [ai-fresshplate.vercel.app](https://ai-fresshplate.vercel.app)
📘 **API docs:** [ai-fresshplate.onrender.com/api/docs/](https://ai-fresshplate.onrender.com/api/docs/)

---

## What it does

FreshPlate solves two problems in one place:

1. **Food ordering** — browse the menu, build a cart, place an order and follow it from
   *placed* to *delivered*.
2. **Food rescue** — a donor lists surplus food with a pickup window, an admin reviews it,
   and a rescue centre collects it instead of it being thrown away.

---

## Features

### Ordering
- Cart with validated quantities, per-item limits and live totals
- Transactional order placement — the order, its items and the cleared cart all succeed together or none of them do
- Price snapshots on every order item, so later menu price changes never rewrite order history
- Customers can cancel their own order while it is still pending or confirmed
- Live status tracking that refreshes itself while an order is on the way

### Food rescue
- Donors list surplus food with quantity, pickup address, pickup time and expiry
- Enforced 3-step lifecycle: `pending → approved → picked_up → distributed`
- Food past its expiry time cannot be approved or sent out
- Public directory of rescue centres

### AI assistant
- Google Gemini, grounded with the live menu and the signed-in user's recent orders
- Guardrails against inventing dishes, prices or order statuses
- Bounded conversation history to keep token cost and latency predictable
- Per-user rate limiting and a graceful message when the provider is unavailable

### Security & access control
- JWT authentication with refresh-token rotation and blacklisting on logout
- Three roles — admin, customer, donor — enforced by reusable DRF permission classes
- Admin accounts can only be created through `createsuperuser` or the Django admin, never through public sign-up
- Rate limiting on auth endpoints to slow down brute-force attempts
- Django's password validators, HTTPS/HSTS and secure cookies in production
- All API data escaped before rendering in the frontend

### Engineering
- State-machine validation on order and donation status changes
- Row-level locking and `F()` expressions to avoid race conditions under concurrent orders
- `select_related` / `prefetch_related` / `annotate` to remove N+1 queries
- Database indexes on the columns the app actually filters by
- OpenAPI schema and Swagger UI generated from the code
- One-command menu seeding for a fresh database

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6, Django REST Framework, SimpleJWT, drf-spectacular |
| Database | PostgreSQL (SQLite fallback for quick local runs) |
| AI | Google Gemini via the `google-genai` SDK |
| Frontend | HTML5, CSS3, vanilla JavaScript (Fetch API) |
| Deployment | Render (API + PostgreSQL), Vercel (frontend), WhiteNoise, Gunicorn |

---

## Project structure

```
FreshPlate/
├── backend/
│   ├── freshplate/        # settings, root urls, health check, API docs
│   ├── users/             # custom user model, auth, role permission classes
│   ├── food/              # categories, menu items, seed_menu command
│   ├── orders/            # cart, orders, status workflow
│   ├── donations/         # food rescue, rescue centres
│   ├── chatbot/           # Gemini service layer + chat sessions
│   ├── build.sh           # Render build script
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── css/style.css
    ├── javascript/main.js # API client, auth, shared helpers
    └── *.html             # index, menu, cart, orders, donation, chatbot, dashboard, login, register
```

---

## Getting started

### Prerequisites
- Python 3.12+
- A Google Gemini API key (optional — everything except the chatbot works without it)
- VS Code with the Live Server extension, for the frontend

### Backend

```bash
git clone https://github.com/AshishChaubey2003/Ai_Fresshplate.git
cd Ai_Fresshplate/backend

python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env
```

Open `.env` and set `SECRET_KEY` and `GEMINI_API_KEY`. Leave `DATABASE_URL` empty to use
SQLite locally.

```bash
python manage.py migrate
python manage.py seed_menu      # fills the menu with 20 sample dishes
python manage.py createsuperuser
python manage.py runserver
```

- API docs → http://127.0.0.1:8000/api/docs/
- Admin → http://127.0.0.1:8000/admin/

### Frontend

Right-click `frontend/index.html` in VS Code → **Open with Live Server**.
It runs on port 5500 and points at the local API automatically.

### Seeding the menu

```bash
python manage.py seed_menu                 # 20 dishes across 5 categories
python manage.py seed_menu --with-images   # also pull a random food photo per dish
python manage.py seed_menu --reset         # drop unused dishes first
```

Safe to run repeatedly — it updates existing dishes rather than duplicating them, and it
never deletes a dish that appears in someone's order history.

---

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Required whenever `DEBUG=False` |
| `DEBUG` | `True` locally, `False` in production |
| `DATABASE_URL` | PostgreSQL connection string; empty means SQLite |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins |
| `GEMINI_API_KEY` | Google Gemini key |
| `GEMINI_MODEL` | Defaults to `gemini-flash-latest` |
| `JWT_ACCESS_MINUTES` / `JWT_REFRESH_DAYS` | Token lifetimes |
| `DELIVERY_CHARGE` | Flat delivery fee |
| `MAX_CART_ITEM_QUANTITY` | Per-item cart limit |

See [`backend/.env.example`](backend/.env.example) for the full list.

---

## API overview

Full interactive documentation lives at `/api/docs/`.

| Method | Endpoint | Access |
|--------|----------|--------|
| `POST` | `/api/users/register/` · `/api/users/login/` | Public |
| `POST` | `/api/users/logout/` · `/api/users/token/refresh/` | Auth |
| `GET` `PATCH` | `/api/users/profile/` | Auth |
| `GET` | `/api/users/all/` | Admin |
| `GET` | `/api/food/items/` · `/api/food/categories/` · `/api/food/rescue/` | Public |
| `POST` `PATCH` `DELETE` | `/api/food/items/create/` · `/api/food/items/<id>/update/` | Admin |
| `GET` `POST` `DELETE` | `/api/orders/cart/` | Auth |
| `PATCH` `DELETE` | `/api/orders/cart/item/<id>/` | Auth |
| `POST` | `/api/orders/place/` | Auth |
| `GET` | `/api/orders/my-orders/` · `/api/orders/my-orders/<id>/` | Auth |
| `POST` | `/api/orders/my-orders/<id>/cancel/` | Auth |
| `GET` `PATCH` | `/api/orders/all/` · `/api/orders/<id>/status/` | Admin |
| `POST` `GET` | `/api/donations/create/` · `/api/donations/my-donations/` | Donor |
| `GET` `PATCH` | `/api/donations/all/` · `/api/donations/<id>/status/` | Admin |
| `GET` `POST` | `/api/donations/rescue-centers/` · `/api/donations/rescue-centers/create/` | Public · Admin |
| `GET` `POST` | `/api/chatbot/` | Auth |
| `DELETE` | `/api/chatbot/session/<id>/delete/` | Auth |
| `GET` | `/api/health/` | Public |

---

## Roles

| Role | What they can do |
|------|------------------|
| **Customer** | Browse the menu, manage a cart, place and cancel orders, use the assistant |
| **Donor** | Everything a customer can, plus listing surplus food for rescue |
| **Admin** | Manage the menu, move orders and donations through their lifecycles, view users |

Sign-up offers customer and donor only. Admin accounts are created with
`python manage.py createsuperuser`.

---

## Deployment

**Backend (Render)**
- Root directory: `backend`
- Build command: `./build.sh`
- Start command: `gunicorn freshplate.wsgi:application`
- Environment: `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`,
  `GEMINI_API_KEY`, `PYTHON_VERSION=3.12.7`

**Frontend (Vercel)** — deploy the `frontend/` folder as a static site.

> **Media note:** Render's disk is wiped on every deploy, so uploaded images do not
> survive. Every image field has an `image_url` companion — paste a hosted photo link
> there instead. For real production uploads, move to S3 or Cloudinary via
> `django-storages`.

---

## Design decisions worth knowing

- **Money is always `Decimal`.** Mixing `Decimal` with `float` raises `TypeError` in Python,
  which is exactly what used to break order placement.
- **Deleting a dish doesn't delete order history.** `OrderItem.food_item` uses `PROTECT`,
  and the admin delete endpoint hides a dish instead of removing it once it has been ordered.
- **Status changes follow a state machine.** The API rejects jumps like
  `pending → delivered`, on both orders and donations.
- **The AI is grounded, not free-form.** The system prompt carries the live menu and the
  user's recent orders, so recommendations and status answers come from real data.
- **The frontend never trusts API text.** Everything is escaped before it becomes HTML —
  a donor's food name cannot run script in an admin's browser.

---

## Roadmap

- [ ] Online payments (Razorpay/Stripe) with webhook verification
- [ ] Image uploads to Cloudinary with multipart forms
- [ ] Pagination on admin lists
- [ ] Automated test suite in CI
- [ ] Move JWTs from `localStorage` to HttpOnly cookies
- [ ] React rewrite of the frontend with shared components

---

## License

MIT

---

<p align="center">
  Built by <a href="https://github.com/AshishChaubey2003">Ashish Kumar Chaubey</a> — B.Tech CSE 2025
</p>
<p align="center">
  <a href="https://www.linkedin.com/in/ashishchaubey2dec/">LinkedIn</a> ·
  <a href="https://personal-portfolio-website-one-azure.vercel.app/">Portfolio</a> ·
  <a href="mailto:sashishchaubey1234@gmail.com">Email</a>
</p>
