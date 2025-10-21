from fastapi import FastAPI

app = FastAPI(title="AI TODO + Pomodoro", version="0.1.0")

@app.get("/")
def root():
    return {"message": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

for r in app.routes:
    print(r.path, r.methods)
