# Task Management Project

## Overview

This project is a Django-based task management application designed to help users manage their tasks efficiently. The application allows users to create, read, update, and delete tasks.

## Project Structure

The project follows the standard Django structure, which includes the following key components:

- **`backend/`**: The main project directory.

  - **`manage.py`**: A command-line utility for interacting with the project.
  - **`backend/`**: The main application directory containing settings and configurations.
    - **`settings.py`**: Configuration for the Django project, including database settings and installed apps.
    - **`urls.py`**: URL routing configuration.
    - **`wsgi.py`**: WSGI configuration for deployment.

- **`tasks/`**: The app responsible for task management.
  - **`migrations/`**: Directory for database migrations.
  - **`models.py`**: Contains the Task model definition.
  - **`admin.py`**: Configuration for the Django admin interface related to tasks.

## Getting Started

### Prerequisites

- Python 3.x
- Django 5.x
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd task_management_project
   ```
