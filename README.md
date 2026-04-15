# GlamBook — Django Salon Booking App

A salon management and booking application built with Django. Supports three roles: Customer, Staff, and Admin.

## Prerequisites

- Python 3.14.3
- pip

## Setup & Run

**1. Create and activate a virtual environment**

```bash
python3 -m venv .venv
```

- macOS / Linux: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Apply migrations**

This creates the database and seeds the default users.

```bash
python manage.py migrate
```

**4. Run the development server**

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Default Accounts

| Role     | Username    | Password    |
|----------|-------------|-------------|
| Admin    | `admin`     | `admin`     |
| Staff    | `staff1`    | `staff1`    |
| Customer | `customer1` | `customer1` |

The admin panel is available at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
