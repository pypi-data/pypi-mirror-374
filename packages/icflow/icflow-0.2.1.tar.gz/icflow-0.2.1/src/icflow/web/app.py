import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from icflow.session import app as session_app
from icflow.session.app import system_init

from .views import user, product, unit, dataset

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(user.router)
app.include_router(product.router)
app.include_router(dataset.router)
app.include_router(unit.router)


_INDEX = """
<html>
<body>
<p><a href="/user">Users</a></p>
<p><a href="/units">Units</a></p>
<p><a href="/products">Products</a></p>
<p><a href="/datasets">Datasets</a></p>
</body>
</html>
"""


@app.get("/")
async def root():
    return HTMLResponse(content=_INDEX, status_code=200)


def launch(app_name: str = "icflow"):

    # Let FastAPI handle threads and db sessions
    db_connect_args = {"check_same_thread": False}

    logger.info("Initializing app")

    session_app.app_init(name=app_name, db_connect_args=db_connect_args)
    system_init()

    logger.info("Initializing web app")

    uvicorn.run(app, host="0.0.0.0", port=8000)
