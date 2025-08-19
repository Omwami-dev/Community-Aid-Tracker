# 🌍 Community Aid Tracker API

The **Community Aid Tracker API** is a Django REST Framework project developed for the **Innocious Foundation**.  
It helps manage community aid projects, donations, beneficiaries, and volunteers while ensuring secure role-based access and transparent reporting.

---

## 🚀 Features
- **Authentication & Authorization** (custom user model with roles)
- **Project Management** (create, update, track progress)
- **Donations** (track donor contributions — visible to admins only)
- **Beneficiaries** (register and assign to projects)
- **Volunteers** (track user participation in projects)
- **Reporting** (generate useful insights)
- **Future Integrations**:
  - 💳 Payments (Flutterwave)  
  - ✉️ Email Notifications (SendGrid)  
  - 🗺️ Maps (Mapbox)

---

## 📂 Project Structure
community_aid_tracker/             # Root folder (my repo)
│
├── community_aid/                 # Django project config folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Global settings (DB, apps, middleware, DRF, etc.)
│   ├── urls.py                     # Root URL router
│   └── wsgi.py
│
├── core/                          # Main app (where models & API live)
│   ├── __init__.py
│   ├── admin.py                    # Model admin configuration
│   ├── apps.py
│   ├── models.py                   # User, Project, Donation, Beneficiary, Volunteer
│   ├── serializers.py              # DRF serializers
│   ├── views.py                    # API views (CRUD, permissions, filtering)
│   ├── urls.py                     # App-level URLs
│   ├── permissions.py              # Custom role-based permissions
│   └── tests.py                    # Unit tests
│
├── requirements.txt                # Project dependencies
├── manage.py                       # Django CLI utility
└── README.md                       # Documentation (my guide)
