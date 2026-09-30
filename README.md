# SafaiSync — Django + DRF Version

This is the simplified SafaiSync stack requested for the project:

| Layer | Technology |
|---|---|
| Backend | Django + Django REST Framework |
| Database | SQLite (development) |
| Frontend | HTML + CSS + Bootstrap + JavaScript |
| Maps | Leaflet.js + OpenStreetMap |
| Charts | Chart.js |

## Features
- Citizen registration/login
- Secure Django authentication
- Report waste issues
- Complaint reference IDs
- Complaint status/history
- Waste pickup requests
- Leaflet map for selecting complaint coordinates
- Admin dashboard
- Chart.js analytics
- Admin complaint/pickup status management
- Waste awareness section
- Django admin
- Frontend + API validation

## Setup on Windows

Open PowerShell in the `SafaiSync_Django` folder.

### 1. Create virtual environment
```powershell
python -m venv venv
```

### 2. Activate it
```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install packages
```powershell
pip install -r requirements.txt
```

### 4. Create database
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create demo accounts
```powershell
python seed_demo.py
```

Demo:
- Admin: `admin` / `Admin@123`
- Citizen: `citizen` / `Citizen@123`

### 6. Run
```powershell
python manage.py runserver
```

Open:
`http://127.0.0.1:8000/`

## API
- GET `/api/health/`
- GET `/api/me/`
- `/api/reports/`
- `/api/pickups/`
- `/api/awareness/`
- GET `/api/admin/stats/`

The API uses Django session authentication. Browser requests automatically send the CSRF token.

## PostgreSQL/MySQL later
For the hackathon/demo, SQLite keeps setup simple. The database can later be switched to PostgreSQL or MySQL by changing `DATABASES` in `safaisync/settings.py` and installing the relevant Django database driver.

## Map
Leaflet is used with OpenStreetMap tiles. No paid API key is required for the basic map implementation.

## Validation
Validation is implemented at:
- Django forms
- DRF serializers
- Django model field validators
- Browser HTML attributes where appropriate

This protects the application even if frontend validation is bypassed.


## If Report / Pickup says "Forbidden (CSRF cookie not set)"
This version explicitly sets a CSRF cookie on pages containing API forms and sends the token in the `X-CSRFToken` header. Restart the Django server after updating the files.

Test API connectivity:
`http://127.0.0.1:8000/api/health/`

Expected:
```json
{"ok": true, "service": "SafaiSync Django API"}
```

If the browser has an old session, log out and log in again after restarting the server.


## Recent fixes
- Dashboard now correctly handles Django REST Framework paginated responses.
- Awareness and Admin pages also handle paginated API responses.
- Report map now uses OpenTopoMap tiles instead of the OpenStreetMap volunteer tile endpoint that can return HTTP 403 for excessive/automated usage.
- Map click still fills latitude and longitude.
- If map tiles are temporarily unavailable, latitude/longitude can still be entered manually.


## Separate Roles

SafaiSync now has three completely separate application portals:

### Citizen
- Login: `/citizen-login/`
- Register: `/register/`
- Report waste issues
- Request pickups
- Track own complaints/pickups
- View awareness content

Demo: `citizen / Citizen@123`

### Garbage Collector
- Login: `/collector-login/`
- Dashboard: `/collector-dashboard/`
- Sees only work assigned by Admin
- Updates assigned complaint status
- Updates assigned pickup status
- Cannot access citizen reporting or admin analytics

Demo: `collector / Collector@123`

### Admin
- Login: `/admin-login/`
- Dashboard: `/admin-dashboard/`
- System-wide complaint/pickup management
- Assign work to garbage collectors
- Analytics
- Django admin available at `/admin/`

Demo: `admin / Admin@123`

Citizen registration always creates a **Citizen** account. Collector and Admin accounts are not created through the public registration form.

## CSRF login fix
The separate role login pages use `ensure_csrf_cookie` on the login view itself. This prevents the Django 5.2 `User object has no attribute COOKIES` error during login.
