from fastapi import FastAPI

from fram.api.routes import health, media

app = FastAPI(title="Fram API", version="0.1.0")
app.include_router(health.router)
app.include_router(media.router)

