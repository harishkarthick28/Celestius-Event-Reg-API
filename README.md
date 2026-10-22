# Celestius Event Registration API

A backend API for managing registrations for the Celestius Backend Development Workshop, built using Python, FastAPI, and SQLite.

## Project Overview

This project provides a backend system that allows students to register for an event and enables organizers to retrieve registration information, manage registrations, and view event statistics.

**Event:** Backend Development Workshop  
**Event Date:** 20 October 2026  
**Maximum Capacity:** 50 participants

## Features

- Student registration with name, email, and optional college/department.
- Automatic recording of registration timestamps.
- Duplicate email detection.
- Input validation and appropriate HTTP error responses.
- Event capacity enforcement.
- Retrieval of all registrations and individual registration details.
- Deletion of registrations by ID.
- Organizer summary with registration totals, available seats, capacity percentage, registrations received today, and department breakdown.
- Persistent storage using SQLite.

## Technology Stack

- **Python** — programming language
- **FastAPI** — API framework
- **Uvicorn** — ASGI server
- **SQLite** — database
- **Swagger UI** — interactive API documentation

## Project Structure

```text
Celestius/
├── main.py
├── database.py
├── registrations.db
├── requirements.txt
└── README.md
```
`registrations.db` is created automatically when the application initializes the database. The database file may not exist until the application has been run.

## Setup and Installation

### 1. Clone or download the project

Open the project folder in VS Code.

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Start the server

Run this command from the directory containing `main.py`:

```powershell
python -m uvicorn main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/register` | Register a student |
| GET | `/registrations` | Retrieve all registrations and seat statistics |
| GET | `/registrations/{registration_id}` | Retrieve one registration |
| DELETE | `/registrations/{registration_id}` | Delete a registration |
| GET | `/organizer/summary` | Retrieve event analytics |

## Example: Register a Student

**Request**

`POST /register`

```json
{
  "name": "Harish Karthick",
  "email": "harishkarthick@example.com",
  "college_department": "CSBS"
}
```

The college/department field is optional.

A successful registration returns HTTP `201 Created`, together with the saved registration details and generated ID.

## Organizer Summary

`GET /organizer/summary`

The response includes:

- Total registrations
- Event capacity
- Available seats
- Percentage of capacity used
- Registrations received today
- Registration breakdown by department
- Capacity status: `OPEN`, `NEAR_CAPACITY`, or `FULL`

The summary is calculated from the current database records.

## HTTP Status Codes

| Status code | Meaning |
|---|---|
| `200 OK` | Request successful |
| `201 Created` | Registration created successfully |
| `404 Not Found` | Registration does not exist |
| `409 Conflict` | Duplicate registration or event capacity reached |
| `422 Unprocessable Entity` | Invalid or missing input |

## Database and Data Persistence

The application stores registration records in SQLite. Data remains available after the server is restarted, provided the same database file is retained and the application connects to it.

Registration IDs are unique identifiers and may contain gaps after records are deleted.

## Testing

The API can be tested through the interactive Swagger UI at `/docs`.

Recommended test cases include:

1. Register a student successfully.
2. Attempt registration with a duplicate email.
3. Submit invalid or missing required information.
4. Verify that the event rejects registrations when capacity is reached.
5. Retrieve all registrations.
6. Retrieve an existing registration and a nonexistent ID.
7. Delete an existing registration and attempt to delete it again.
8. Verify the organizer summary and seat counts.
9. Restart the server and confirm that registrations persist.

## Future Improvements

- Automated API tests using `pytest`.
- Organizer authentication and authorization.
- Search, filtering, and pagination for registrations.
- More robust email validation and improved database transaction handling.

## Learning Outcomes

This project provided practical experience with REST APIs, HTTP status codes, request validation, relational database operations, SQL queries, error handling, and backend application development using FastAPI.

---

**Project:** Celestius Event Registration API  
**Purpose:** Backend development recruitment task
