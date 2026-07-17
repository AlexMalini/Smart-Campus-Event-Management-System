# Smart Campus Event Management System

## 📖 Project Overview

The **Smart Campus Event Management System** is a web-based application developed using **Python Flask** and **MySQL** to simplify and automate college event management. The system provides separate portals for students and administrators, allowing efficient event creation, registration, attendance management, and certificate generation.

This project replaces manual event management with a secure, user-friendly, and digital platform.

---

## ✨ Features

### 👨‍🎓 Student Module
- Student Registration
- Student Login
- Forgot Password using Email OTP
- View Available Events
- Register for Events
- View My Registrations
- View & Edit Student Profile
- QR Code Based Attendance
- Download Participation Certificate

### 👨‍💼 Admin Module
- Admin Login
- Create Events
- View, Edit and Delete Events
- View Student Registrations
- Manage Attendance
- Generate PDF Certificates
- View Analytics Dashboard

---

## 📊 Analytics Dashboard

The dashboard displays:

- Total Students
- Total Events
- Total Registrations
- Present Attendance Count
- Attendance Pie Chart
- Registration Statistics Bar Chart

---

## 🔐 Security Features

- Email OTP Password Recovery
- OTP Expiry (5 Minutes)
- Session Management
- Duplicate Event Registration Prevention
- Duplicate Attendance Prevention

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Python Libraries
- Flask-Mail
- qrcode
- ReportLab
- MySQL Connector

### Development Tools
- Visual Studio Code
- XAMPP
- Git
- GitHub

---

## 📂 Project Structure

```
SmartCampusEventManagement/
│
├── app.py
├── config.py
├── certificates/
├── qr_codes/
├── static/
│   ├── css/
│   └── images/
├── templates/
└── venv/
```

---

## 🚀 Modules

- Student Registration & Login
- Admin Login
- Forgot Password with Email OTP
- Event Management
- Event Registration
- QR Code Generation
- QR Attendance
- Attendance Management
- PDF Certificate Generation
- Student Profile
- Analytics Dashboard

---

## 💻 Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/Smart-Campus-Event-Management-System.git
```

### Navigate to the Project Folder

```bash
cd Smart-Campus-Event-Management-System
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Configure MySQL

- Create a MySQL database named **smartcampus**
- Import the project database
- Update database credentials in `config.py`

### Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📷 Screenshots

- Home Page
- Student Registration
- Student Login
- Student Dashboard
- Admin Dashboard
- Event Creation
- Event Registration
- QR Attendance
- Attendance Management
- PDF Certificate
- Analytics Dashboard

---

## 🎯 Future Enhancements

- Online Payment Gateway Integration
- Password Hashing
- Email Notifications
- SMS Notifications
- Mobile Application
- Cloud Deployment
- Multi-Admin Support
- Biometric Attendance

---

## 👩‍💻 Developer

**Malini A**

Bachelor of Engineering (Computer Science and Engineering)

---

## 📄 License

This project is developed for educational and academic purposes.
