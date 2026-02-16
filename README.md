# Student Success Hub

**Student Success Hub** is a comprehensive platform designed to support students in their academic and professional journey. It bridges the gap between students, alumni, and resources, fostering a collaborative environment for growth and success.

## 🚀 Features

*   **User Accounts (`accounts`)**: Secure user authentication and detailed profile management.
*   **Dashboard (`dashboard`)**: A personalized landing page providing a snapshot of activities and updates.
*   **Alumni Connect (`alumni`)**: Connect with alumni for mentorship and networking opportunities.
*   **Chat (`chat`)**: Real-time messaging system to facilitate communication between users.
*   **Doubts (`doubts`)**: A Q&A platform where students can ask questions and get answers from peers and mentors.
*   **Guidance (`guidance`)**: Dedicated section for mentorship and career guidance.
*   **Hackathons (`hackathons`)**: Track, join, and manage hackathon participation.
*   **Resources (`resources`)**: Access a curated library of study materials and educational resources.
*   **Roadmaps (`roadmaps`)**: Visual learning paths to guide students through various technologies and skills.
*   **Modern UI**: Built with **Tailwind CSS** for a responsive and visually appealing interface.

## 🛠️ Tech Stack

*   **Backend**: Django (Python)
*   **Frontend**: HTML, Tailwind CSS, JavaScript
*   **Database**: SQLite (Development) / PostgreSQL (Production)
*   **Styling**: `django-tailwind`

## ⚙️ Installation & Setup

Follow these steps to set up the project locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NxAdx/Student-Success-Hub.git
    cd Student-Success-Hub
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Node.js dependencies (for Tailwind CSS):**
    Ensure you have Node.js installed, then run:
    ```bash
    python manage.py tailwind install
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    # Start the Tailwind watcher (in a separate terminal)
    python manage.py tailwind start

    # Start the Django server
    python manage.py runserver
    ```

7.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## 📸 Screenshots

*(Add screenshots of your application here)*

## 🤝 Contribution

Contributions are welcome! Please fork the repository and submit a pull request.