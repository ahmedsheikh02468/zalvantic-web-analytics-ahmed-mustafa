from fastapi import FastAPI

app = FastAPI(title="Zalvantic Web Analytics API", version="1.0.0")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Zalvantic Web Analytics API is running successfully!"}