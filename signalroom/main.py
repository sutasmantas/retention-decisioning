from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse

from signalroom.config import settings
from signalroom.schemas import PolicyRequest, ScoreRequest
from signalroom.service import RetentionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retention = RetentionService(settings)
    yield


app = FastAPI(
    title="SignalRoom Retention Decisioning API",
    version="1.0.0",
    description=(
        "Reproducible churn scoring, heterogeneous treatment-effect estimation and "
        "capacity-aware retention policy simulation."
    ),
    lifespan=lifespan,
)


def service(request: Request) -> RetentionService:
    return request.app.state.retention


@app.get("/api/health")
def health(request: Request):
    current = service(request)
    return {
        "status": "ok",
        "model_status": current.health_status(),
        "model_version": "churn-logit-1.0",
    }


@app.get("/api/summary")
def summary(request: Request):
    return service(request).summary()


@app.get("/api/accounts")
def accounts(request: Request, limit: int = Query(default=100, ge=1, le=500)):
    return {"accounts": service(request).list_accounts(limit)}


@app.get("/api/accounts/{account_id}")
def account(account_id: str, request: Request):
    result = service(request).get_account(account_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return result


@app.post("/api/score")
def score(payload: ScoreRequest, request: Request):
    return service(request).score(payload)


@app.put("/api/policy")
def save_policy(payload: PolicyRequest, request: Request):
    return service(request).save_policy(payload)


@app.get("/api/policy/curve")
def curve(
    request: Request,
    capacity: int = Query(default=50, ge=1, le=500),
):
    return {"curve": service(request).curve(capacity)}


@app.get("/api/monitoring")
def monitoring(request: Request):
    return service(request).monitoring()


@app.get("/")
def root():
    return FileResponse("index.html")


@app.get("/styles.css")
def stylesheet():
    return FileResponse("styles.css", media_type="text/css")


@app.get("/app.js")
def javascript():
    return FileResponse("app.js", media_type="text/javascript")
