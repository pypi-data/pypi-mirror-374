"""main.py."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from strangeworks_core.errors.error import StrangeworksError

from .middleware import RequestContextMiddleware
from .routes import router

logging.basicConfig(level=logging.INFO)
gql_logger = logging.getLogger("gql.transport.requests")
gql_logger.setLevel(logging.DEBUG)

app = FastAPI()


@app.exception_handler(StrangeworksError)
async def http_exception_handler(
    request: Request, exc: StrangeworksError
) -> JSONResponse:
    """Exception handler for StrangeworksError exceptions.

    More info on how this works here: https://tinyurl.com/2hfr9fwj

    Parameters
    ----------
    requst: Request
        request object.
    exc: StrangeworksError
        StrangeworksError exception.

    Return
    ------
    :JSONResponse
        The exception represented as a JSONResponse object.
    """
    logging.exception(exc)
    return JSONResponse(status_code=400, content={"error": str(exc.message)})


# add routers
app.add_middleware(RequestContextMiddleware)

app.include_router(router)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}
