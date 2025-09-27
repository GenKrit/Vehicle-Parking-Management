# Vehicle Parking System – MAD1 Project

A responsive web-based parking management system built using **Flask** and **Bootstrap 5**. It provides separate interfaces for **admin** and **user** roles, supports live bookings, spot availability tracking, and visual analytics.

---

## 🔧 Features

### 👤 User Side
- Register and login securely
- Book parking spots based on location and availability
- View current active bookings
- View past bookings with cost summary
- Interactive charts for booking history

### 🔐 Admin Side
- Admin login and dashboard
- Add, edit, and delete parking lots
- Auto-create spots for new lots
- View all users and bookings
- Earnings and occupancy charts

### Admin Login
- Email: admin@admin.com  
- Password: admin123  

---

## 🗂️ Folder Structure

```project-root/
├── app.py # Main entry point```
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── controllers/
│ ├── admin_routes.py # Admin routes and views
│ └── user_routes.py # User routes and views
├── models/
│ └── db_models.py # Database schema
├── templates/ # All HTML templates
│ ├── base.html # Shared layout
│ ├── admin_login.html
│ ├── admin_dashboard.html
│ ├── user_login.html
│ ├── register.html
│ └── ...
├── static/ # Custom CSS, JS, logo etc.
│ └── ...```

---

## TO Run

pip install -r requirements.txt
Run the app

Run:
python app.py
Open your browser at http://localhost:5000

🧪 Tech Stack
Python 3.9+
Flask
SQLite (via SQLAlchemy)
HTML5, CSS3, Bootstrap 5
Chart.js for analytics

🙋 Author
Shashwat - 22f2000067
