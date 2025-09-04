"""callable.py."""

import asyncio

from fastapi import APIRouter, Request

from .handler import execute_request
from .middleware import RequestParams
from .types import SubmitRequest

router: APIRouter = APIRouter(prefix="/jobs", tags=["Callables"])


@router.post("/submit")
async def run_callable(request: Request, submit_request: SubmitRequest):
    """Run Callable Implementation.

    Wraps app_fn as a coroutine to allow everything to run async.
    """
    params: RequestParams = request.state.params
    loop = asyncio.get_running_loop()

    def fn():
        return execute_request(
            ctx=params.ctx,
            app_fn=params.callable_fn,
            estimator_fn=params.estimator_fn,
            cost_fn=params.calculator_fn,
            submit_request=submit_request,
            job_tags=params.job_tags,
        )

    return await loop.run_in_executor(None, fn)
