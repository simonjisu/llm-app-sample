import random
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine import chat_response
from models import UserQuery

load_dotenv()

app = FastAPI()

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/qa")
async def qa(query: UserQuery):
    response = chat_response(query.query)
    return {
        "response": response
    }

@app.get("/test")
async def test():
    return {
        "id": random.randint(1, 10),
        "name": "Test API"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)