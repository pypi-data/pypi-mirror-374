"""common.py."""

import json  # noqa E402
from dataclasses import dataclass

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sw_product_lib.platform.gql import ProductAPI
from sw_product_lib.service import DEFAULT_PLATFORM_BASE_URL, RequestContext

from . import (
    AppFunction,
    CallableImplenmetation,
    CostCalculator,
    CostEstimator,
    DefaultJobTags,
    _cfg,
)

ignore_paths = ["/docs", "/openapi.json", "/"]


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Add RequestContext to the request."""

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    async def dispatch(self, request, call_next):  # noqa
        if request.url.path in ignore_paths:
            return await call_next(request)

        request.state.params = RequestParams.from_request(request)
        return await call_next(request)


@dataclass
class RequestParams:
    """Class for items needed to handle a request."""

    ctx: RequestContext
    callable_fn: AppFunction
    estimator_fn: AppFunction
    calculator_fn: AppFunction
    job_tags: list[str] | None

    @classmethod
    def from_request(cls, request: Request) -> "RequestParams":
        ctx = RequestContext.from_request(request=request)
        ctx.api = ProductAPI(
            api_key=_cfg.get("api_key", profile="platform"),
            base_url=_cfg.get("api_url", "platform") or DEFAULT_PLATFORM_BASE_URL,
        )
        return cls(
            ctx=ctx,
            callable_fn=CallableImplenmetation,
            estimator_fn=CostEstimator,
            calculator_fn=CostCalculator,
            job_tags=DefaultJobTags,
        )
