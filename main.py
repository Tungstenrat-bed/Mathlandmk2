import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# Data model matching your Unity JSON payload
class StudentResult(BaseModel):
    student_id: str
    question: str
    time_taken: float
    is_correct: bool

# Determine performance status based on timing and accuracy
def calculate_status(time_taken: float, is_correct: bool) -> str:
    if not is_correct:
        return "Very Bad" if time_taken < 1.0 else "Bad"
    if time_taken < 2.0:
        return "Expert"
    elif time_taken < 4.0:
        return "Good"
    else:
        return "Normal"

# THIS DECORATOR DEFINES THE OPERATION
@app.post("/submit-result")
def submit_result(result: StudentResult):
    status = calculate_status(result.time_taken, result.is_correct)
    
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS math_results (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50),
                question VARCHAR(50),
                time_taken FLOAT,
                is_correct BOOLEAN,
                status VARCHAR(20)
            )
        """)
        
        cursor.execute("""
            INSERT INTO math_results (student_id, question, time_taken, is_correct, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (result.student_id, result.question, result.time_taken, result.is_correct, status))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Data saved successfully", "calculated_status": status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))