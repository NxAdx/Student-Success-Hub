# Student Success Hub

[![Render](https://img.shields.io/badge/Render-Live_Demo-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://student-success-hub.onrender.com/)

**Student Success Hub** is a comprehensive platform designed to empower students in their academic and professional journey. It bridges the gap between students, alumni, and resources, fostering a collaborative environment for growth and success.

## 📖 Table of Contents

*   [Features](#-features)
*   [Tech Stack](#-tech-stack)
*   [Project Structure](#-project-structure)
*   [Installation & Setup](#-installation--setup-local-development)
*   [Deployment](#-deployment)
*   [Contributing](#-contributing)
*   [License](#-license)
*   [Screenshots](#-screenshots)

## 🚀 Features

*   **User Accounts (`accounts`)**: Secure user authentication, profile management, and role-based access.
*   **Dashboard (`dashboard`)**: A personalized central hub providing a snapshot of activities, notifications, and updates.
*   **Alumni Connect (`alumni`)**: Bridge the gap between current students and alumni for mentorship and networking.
*   **Chat (`chat`)**: Real-time messaging system to facilitate direct communication between users.
*   **Doubts (`doubts`)**: A collaborative Q&A platform where students can ask questions and receive answers from peers and mentors.
*   **Guidance (`guidance`)**: Dedicated section for long-term mentorship and career guidance resources.
*   **Hackathons (`hackathons`)**: precise tracking of hackathons, allowing users to join teams and manage participation.
*   **Resources (`resources`)**: Access a curated library of study materials, notes, and educational resources.
*   **Roadmaps (`roadmaps`)**: Visual interactive learning paths to guide students through various technologies and skills.
*   **Modern UI**: Built with **Tailwind CSS** for a responsive, accessible, and visually appealing interface.

## 🛠️ Tech Stack

*   **Backend**: Django 5.0 (Python 3.11+)
*   **Frontend**: HTML5, Tailwind CSS, JavaScript
*   **Database**: SQLite (Development) / PostgreSQL (Production)
*   **Styling**: `django-tailwind` (Tailwind CSS)
*   **Media Storage**: Cloudinary (Production)
*   **Security**: SSL redirection, HSTS, Secure Cookies, and Clickjacking protection
*   **Reliability**: Custom 404/500 pages and structured production logging
*   **Deployment**: Ready for Render.com

## 📂 Project Structure

Here is an overview of the project's file structure to help you navigate:

```text
Student-Success-Hub/
├── .env                  # Environment variables (Secret!) - Create this file
├── Procfile              # Command to run the app on Render
├── render.yaml           # Render infrastructure as code
├── requirements.txt      # Python dependencies
├── manage.py             # Django command-line utility
├── db.sqlite3            # Local development database
├── student_success_hub/  # Main project configuration (settings, urls, wsgi)
├── theme/                # Tailwind CSS app
├── static/               # Static files (CSS, JS, Images)
├── templates/            # Global HTML templates
│
├── accounts/             # User authentication & profiles
├── dashboard/            # Main user dashboard logic
├── alumni/               # Alumni directory & interactions
├── chat/                 # Real-time chat functionality
├── doubts/               # Q&A forum
├── guidance/             # Mentorship logic
├── hackathons/           # Hackathon tracker
├── resources/            # Educational resources
└── roadmaps/             # Learning paths
```

## ⚙️ Installation & Setup (Local Development)

Follow these steps to set up the project locally on your machine:

### 1. Prerequisites
- **Python 3.11+** installed.
- **Node.js** installed (required for Tailwind CSS).
- **Git** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/NxAdx/Student-Success-Hub.git
cd Student-Success-Hub
```

### 3. Create Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Install Tailwind CSS Dependencies
This project uses `django-tailwind`. You need to install the Node.js dependencies for the theme app.
```bash
python manage.py tailwind install
```

### 6. Environment Configuration
Create a `.env` file in the root directory (same level as `manage.py`) to store secret keys. You can use `.env.example` as a reference if available, or add the following:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
```
*(Note: Never commit your `.env` file to version control)*

### 7. Database Setup
Apply migrations to create the database schema.
```bash
python manage.py migrate
```

### 8. Run the Development Server
You need to run two processes: one for Tailwind CSS (to compile styles) and one for the Django server.


**Terminal 1 (Tailwind Watcher):**
```bash
python manage.py tailwind start
```

**Terminal 2 (Django Server):**
```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`


## 🚀 Deployment

This project is configured for easy deployment on **Render.com**.

1.  Create a new Web Service on Render.
2.  Connect your GitHub repository.
3.  Render should automatically detect the `render.yaml` or `Procfile`.
4.  **Environment Variables**: Add these in the Render dashboard:
    *   `PYTHON_VERSION`: `3.11.6`
    *   `SECRET_KEY`: (Generate a strong random key)
    *   `WEB_CONCURRENCY`: `4`
    *   `CLOUDINARY_CLOUD_NAME`: (From your Cloudinary dashboard)
    *   `CLOUDINARY_API_KEY`: (From your Cloudinary dashboard)
    *   `CLOUDINARY_API_SECRET`: (From your Cloudinary dashboard)

> **🚀 Note on Media Storage:**
> This project uses **Cloudinary** for persistent media storage. Unlike Render's ephemeral filesystem, Cloudinary ensures that user-uploaded files (like profile pictures and thumbnails) are saved permanently even after redeployments.

## 🛡️ Production Reliability & Security

The platform is built with professional-grade security and reliability features out of the box:

-   **Automatic SSL/HTTPS**: All traffic is automatically redirected to HTTPS in production using Django's security middleware.
-   **HSTS (HTTP Strict Transport Security)**: Configured to enforce HTTPS for all browser sessions, improving defense against protocol downgrade attacks.
-   **Secure Cookies**: Session and CSRF cookies are marked as `Secure` and `HttpOnly` in production to prevent theft and hijacking.
-   **Clickjacking Protection**: All pages are protected against clickjacking attacks using the `X-Frame-Options: DENY` header.
-   **Custom Error Pages**: Professional 404 (Not Found) and 500 (Server Error) pages are provided to ensure a seamless user experience even when things go wrong.
-   **Structured Logging**: Production logging is automatically configured to help you monitor and troubleshoot your application through the Render dashboard.
-   **Deployment Guards**: The build script (`build.sh`) includes a `check --deploy` command that verifies your settings for production readiness before every deployment.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to:
- Set up your development environment.
- Create branches and Pull Requests.
- **Add Collaborators** to the repository.

## 📄 License

[MIT License](LICENSE)


## 📸 Screenshots

| **Home Page** | ![Home](docs/screenshots/home.png) |
| **Login / Sign Up** | ![Login](docs/screenshots/login.png) |
| **Create Account** | ![Create Account](docs/screenshots/create_account.png) |
| **User Profile** | ![User Profile](docs/screenshots/user_profile.png) |
| **Edit Profile** | ![Edit Profile](docs/screenshots/user_profile_edit.png) |
| **Dashboard** | ![Dashboard](docs/screenshots/dashboard.png) |
| **Admin Panel** | ![Admin Panel](docs/screenshots/admin_panel.png) |
| **Resource Library** | ![Resource Library](docs/screenshots/resource_library.png) |
| **Alumni Network** | ![Alumni Network](docs/screenshots/alumni_network.png) |
| **Alumni Profile** | ![Alumni Profile](docs/screenshots/alumni_profile.png) |
| **Sessions** | ![Sessions](docs/screenshots/sessions.png) |
| **Session Details** | ![Session Details](docs/screenshots/session_details.png) |
| **Roadmaps** | ![Roadmaps](docs/screenshots/roadmaps.png) |
| **Roadmap Details** | ![Roadmap Sample](docs/screenshots/roadmap_sample.png) |
| **Hackathons** | ![Hackathons](docs/screenshots/hackathons.png) |
| **Hackathon Details** | ![Hackathon Details](docs/screenshots/hackathon_details.png) |
| **Messages (Chat)** | ![Messages](docs/screenshots/messages.png) |
| **Support Group** | ![Support Group](docs/screenshots/support_group.png) |
| **Doubts (Q&A)** | ![Doubts](docs/screenshots/doubts.png) |



