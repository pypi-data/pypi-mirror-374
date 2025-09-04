"""handler.py."""

import logging

from strangeworks_core.errors.error import StrangeworksError
from sw_product_lib import service
from sw_product_lib.service import RequestContext
from sw_product_lib.types.job import Job, JobStatus

from . import AppFunction
from .types import SubmitRequest


def execute_request(
    ctx: RequestContext,
    app_fn: AppFunction,
    estimator_fn: AppFunction,
    cost_fn: AppFunction,
    submit_request: SubmitRequest,
    job_tags: list[str] | None = None,
) -> Job:
    """Execute Callable Request."""
    # Even if the job submission fails, there should be a record of it on the platform.
    sw_job: Job = service.create_job(ctx)

    if job_tags:
        logging.debug(f"adding job tags {job_tags}")
        service.add_job_tags(ctx, sw_job.slug, tags=job_tags)

    cost_estimate = estimator_fn(submit_request)
    try:
        if not service.request_job_clearance(ctx=ctx, amount=cost_estimate):
            # did not get clearance. update job status to failed and raise error.
            service.update_job(
                ctx=ctx,
                job_slug=sw_job.slug,
                status=JobStatus.FAILED,
            )
            raise StrangeworksError(
                message=f"Job clearance denied for this resource {ctx.resource_slug}."
            )
    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            status=JobStatus.FAILED,
        )
        raise StrangeworksError(
            message=f"Request to platform for job clearance failed {ctx.resource_slug}."
        ) from err

    try:
        logging.info(f"executing job request (job slug: {sw_job.slug})")
        if submit_request.file_url:
            files = [
                service.get_job_file(ctx=ctx, file_path=f)
                for f in submit_request.file_url
            ]
            submit_request.callable_params["payload"]["files"] = files
        result = app_fn(**submit_request.callable_params)
        logging.info(f"uploading job result (job slug: {sw_job.slug})")
        service.upload_job_artifact(
            result,
            ctx=ctx,
            job_slug=sw_job.slug,
            file_name="result.json",
        )
        logging.info(f"updating job status to COMPLETED (job slug: {sw_job.slug})")
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            status=JobStatus.COMPLETED,
        )
        cost = cost_fn(result)
        logging.info(
            f"creating billing transaction of ${cost} (job slug: {sw_job.slug})"
        )
        try:
            service.create_billing_transaction(
                ctx,
                job_slug=sw_job.slug,
                amount=cost,
                description=f"cost for {sw_job.slug}",
            )
        except Exception as err:
            logging.error(
                f"unable to create billing transaction of {cost} (job slug: {sw_job.slug})"  # noqa
            )
            raise StrangeworksError(message=err) from err
        logging.info(f"completed execution of job request (job slug: {sw_job.slug})")
    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            status=JobStatus.FAILED,
        )
        raise StrangeworksError(message=err) from err

    return sw_job
