import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI() # <-- This is the exact variable Render is looking for!

# ... rest of the code