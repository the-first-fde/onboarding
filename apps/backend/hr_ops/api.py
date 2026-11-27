import os
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from .contracts import HireConfirmedEvent
from .persistence import database, Base, OnboardingCase
from .service import confirm, view, Conflict
from .worker import tick

def create_app(url: str | None = None) -> FastAPI:
    engine, factory = database(url)
    @asynccontextmanager
    async def lifespan(app):
        if os.getenv("ADAPTER_MODE", "mock") != "mock":
            raise RuntimeError("only synthetic mock mode is implemented")
        if engine.dialect.name == "sqlite":
            Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(title="HR Operations · local synthetic demo", lifespan=lifespan)
    app.state.factory = factory

    def hr_actor(authorization: str | None = Header(default=None)) -> str:
        token = os.getenv("DEMO_HR_TOKEN", "")
        if not token or not authorization or not secrets.compare_digest(authorization, "Bearer " + token):
            raise HTTPException(403, "demo HR authorization required")
        return "demo-hr"

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Never echo rejected inputs, including unknown sensitive field names.
        return JSONResponse(status_code=422, content={"detail": "invalid handoff contract"})

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "synthetic-mock", "full_service": False}

    @app.post("/api/hire-confirmations")
    def hire(event: HireConfirmedEvent, actor: str = Depends(hr_actor)):
        try:
            return confirm(factory, event, actor)
        except Conflict:
            raise HTTPException(409, "event/candidate conflict; HR review required")

    @app.get("/api/cases")
    def cases(actor: str = Depends(hr_actor)):
        with factory() as session:
            return [view(session, c) for c in session.scalars(select(OnboardingCase)).all()]

    @app.get("/api/cases/{case_id}")
    def case(case_id: str, actor: str = Depends(hr_actor)):
        with factory() as session:
            c = session.get(OnboardingCase, case_id)
            if not c:
                raise HTTPException(404, "case not found")
            return view(session, c)

    @app.post("/api/mock-worker/tick")
    def run_worker(actor: str = Depends(hr_actor)):
        return {"processed": tick(factory, os.getenv("ADAPTER_MODE", "mock"))}

    return app

app = create_app()
