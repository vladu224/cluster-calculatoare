from fastapi import FastAPI

app = FastAPI(title="Auth Service", root_path="/api/auth")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth" }