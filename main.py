
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3

from database import get_connection, init_db

app = FastAPI(title="Celestius Event Registration API")

# Ensure the database table exists
init_db()

EVENT_CAPACITY = 50


class RegistrationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    college_department: str | None = Field(default=None, max_length=150)


@app.get("/")
def home():
    return {"message": "Celestius backend is running!"}


@app.post("/register", status_code=201)
def register_student(student: RegistrationRequest):
    name = student.name.strip()
    email = student.email.strip().lower()
    college_department = student.college_department

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Name cannot be empty."
        )

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid email address."
        )

    if college_department is not None:
        college_department = college_department.strip() or None

    connection = get_connection()

    try:
        # Check for duplicate registrations
        existing = connection.execute(
            "SELECT id FROM registrations WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="This email is already registered."
            )

        # Check event capacity
        count = connection.execute(
            "SELECT COUNT(*) FROM registrations"
        ).fetchone()[0]

        if count >= EVENT_CAPACITY:
            raise HTTPException(
                status_code=409,
                detail="Event is full."
            )

        # Save the registration
        cursor = connection.execute(
            """
            INSERT INTO registrations
                (name, email, college_department)
            VALUES (?, ?, ?)
            """,
            (name, email, college_department)
        )

        connection.commit()

        registration = connection.execute(
            "SELECT * FROM registrations WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return dict(registration)
    except HTTPException:
        connection.rollback()
        raise

    except sqlite3.IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="A registration with this email already exists."
        )

    finally:
        connection.close()

@app.get("/registrations")
def get_registrations():
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM registrations ORDER BY id"
        ).fetchall()

        return {
            "total_registrations": len(rows),
            "capacity": EVENT_CAPACITY,
            "available_seats": EVENT_CAPACITY - len(rows),
            "registrations": [dict(row) for row in rows]
        }

    finally:
        connection.close()

@app.get("/registrations/{registration_id}")
def get_registration(registration_id: int):
    connection = get_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Registration not found."
            )

        return dict(row)

    finally:
        connection.close()

@app.get("/organizer/summary")
def organizer_summary():
    connection = get_connection()

    try:
        # Get total registrations and registrations received today
        stats = connection.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN date(registered_at, 'localtime') =
                             date('now', 'localtime')
                        THEN 1
                        ELSE 0
                    END
                ) AS today
            FROM registrations
        """).fetchone()

        total = stats["total"]
        registered_today = stats["today"] or 0
        available_seats = max(0, EVENT_CAPACITY - total)

        # Calculate the percentage of capacity filled
        capacity_used_percent = round(
            (total / EVENT_CAPACITY) * 100, 2
        )

        # Decide the event's current capacity status
        if total >= EVENT_CAPACITY:
            status = "FULL"
        elif total >= EVENT_CAPACITY * 0.8:
            status = "NEAR_CAPACITY"
        else:
            status = "OPEN"

        # Count registrations by college/department
        department_rows = connection.execute("""
            SELECT
                COALESCE(
                    NULLIF(TRIM(college_department), ''),
                    'Not specified'
                ) AS department,
                COUNT(*) AS registrations
            FROM registrations
            GROUP BY COALESCE(
                NULLIF(TRIM(college_department), ''),
                'Not specified'
            )
            ORDER BY registrations DESC, department ASC
        """).fetchall()

        return {
            "event": "Backend Development Workshop",
            "total_registrations": total,
            "capacity": EVENT_CAPACITY,
            "available_seats": available_seats,
            "capacity_used_percent": capacity_used_percent,
            "registrations_today": registered_today,
            "status": status,
            "department_breakdown": [
                dict(row) for row in department_rows
            ]
        }

    finally:
        connection.close()

@app.delete("/registrations/{registration_id}")
def delete_registration(registration_id: int):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT id FROM registrations WHERE id = ?",
            (registration_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Registration not found."
            )

        connection.execute(
            "DELETE FROM registrations WHERE id = ?",
            (registration_id,)
        )
        connection.commit()

        return {
            "message": "Registration deleted successfully.",
            "deleted_registration_id": registration_id
        }

    finally:
        connection.close()