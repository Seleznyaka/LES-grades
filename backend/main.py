from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("grades.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher TEXT NOT NULL,
            subject TEXT NOT NULL,
            grade1 INTEGER,
            grade2 INTEGER,
            grade3 INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

class GradeCreate(BaseModel):
    teacher: str
    subject: str
    grade1: Optional[int] = None
    grade2: Optional[int] = None
    grade3: Optional[int] = None

    @field_validator('grade1', 'grade2', 'grade3')
    @classmethod
    def check_grade(cls, v):
        if v is not None and v not in (3, 4, 5):
            raise ValueError('Оценка должна быть 3, 4, 5 или прочерк')
        return v

def calc_avg(g1, g2, g3):
    """Среднее только по реальным оценкам (не None)"""
    grades = [g for g in (g1, g2, g3) if g is not None]
    if not grades:
        return None
    return round(sum(grades) / len(grades), 2)

@app.get("/grades")
def get_grades():
    conn = sqlite3.connect("grades.db")
    items = conn.execute(
        "SELECT id, teacher, subject, grade1, grade2, grade3 FROM grades"
    ).fetchall()
    conn.close()

    result = []
    for r in items:
        avg = calc_avg(r[3], r[4], r[5])
        result.append({
            "id": r[0],
            "teacher": r[1],
            "subject": r[2],
            "grade1": r[3],
            "grade2": r[4],
            "grade3": r[5],
            "avg": avg
        })
    return result

@app.post("/grades")
def add_grade(data: GradeCreate):
    conn = sqlite3.connect("grades.db")
    cursor = conn.execute(
        "INSERT INTO grades (teacher, subject, grade1, grade2, grade3) VALUES (?, ?, ?, ?, ?)",
        (data.teacher, data.subject, data.grade1, data.grade2, data.grade3)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    avg = calc_avg(data.grade1, data.grade2, data.grade3)
    return {
        "id": new_id,
        "teacher": data.teacher,
        "subject": data.subject,
        "grade1": data.grade1,
        "grade2": data.grade2,
        "grade3": data.grade3,
        "avg": avg
    }

@app.put("/grades/{grade_id}")
def update_grade(grade_id: int, data: GradeCreate):
    conn = sqlite3.connect("grades.db")
    conn.execute(
        "UPDATE grades SET teacher=?, subject=?, grade1=?, grade2=?, grade3=? WHERE id=?",
        (data.teacher, data.subject, data.grade1, data.grade2, data.grade3, grade_id)
    )
    conn.commit()
    conn.close()

    avg = calc_avg(data.grade1, data.grade2, data.grade3)
    return {
        "id": grade_id,
        "teacher": data.teacher,
        "subject": data.subject,
        "grade1": data.grade1,
        "grade2": data.grade2,
        "grade3": data.grade3,
        "avg": avg
    }

@app.delete("/grades/{grade_id}")
def delete_grade(grade_id: int):
    conn = sqlite3.connect("grades.db")
    conn.execute("DELETE FROM grades WHERE id=?", (grade_id,))
    conn.commit()
    conn.close()
    return {"ok": True}