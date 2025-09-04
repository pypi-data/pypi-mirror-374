"""__init__.py."""

import inspect
from importlib.util import find_spec, module_from_spec
from typing import Callable, ParamSpec, TypeVar

from strangeworks_core.config.config import Config

_cfg = Config()

# Jobs can be tagged with a list of tags specified by
# STRANGEWORKS_CONFIG_CALLABLE_SVC_JOB_TAGS. The env var should be a list of strings
# to be use for tagging jobs created by the application.
_raw_tags = _cfg.get("job_tags", profile="callable_svc")
DefaultJobTags: list[str] = (
    [] if _raw_tags is None else list(r.strip() for r in _raw_tags.split(","))
)


# better way to provide a parameter spec for a Callable parameter types
# see https://docs.python.org/3/library/typing.html#typing.ParamSpec
T = TypeVar("T")  # can be anything
P = ParamSpec("P")
AppFunction = Callable[P, T]


def _get_callable(module: str, callable_name: str) -> AppFunction:
    """Loads Callable.

    Load the Callable/Function specified by callable_name defined in module.
    Imitates `from module import callable_name` at runtime.

    Parameters
    ----------
    module: str
        fully qualified name of the module where the callable is implemented.
    callable_name: str
        name of the function.

    Returns
    -------
    :AppFunction
        Callable to be used as the implementation of the service.
    """
    mod_spec = find_spec(module)
    if mod_spec is None:
        raise ValueError(f"unable to find the {module} module.")
    mod = module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)

    _functions = inspect.getmembers(mod, inspect.isfunction)

    for name, _fn in _functions:
        if name == callable_name:
            return _fn
    return None


# set up the function that will be called when the service is invoked.

_CALLABLE_NAME = _cfg.get("name", profile="callable_svc")
_CALLABLE_MODULE = _cfg.get("module", profile="callable_svc")
CallableImplenmetation: AppFunction = _get_callable(
    module=_CALLABLE_MODULE, callable_name=_CALLABLE_NAME
)


# default functions
def _default_cost_estimator(*args, **kwargs) -> float:
    return 0.0


def _default_cost_calculator(*args, **kwargs) -> float:
    return 0.0


# set up cost estimator function. default to a function that returns 0.
_COST_ESIMATOR_NAME = _cfg.get("cost_estimator", profile="callable_svc")
_COST_ESIMATOR_MODULE = (
    _cfg.get("cost_estimator_module", profile="callable_svc") or _CALLABLE_MODULE
)
CostEstimator: AppFunction = (
    _get_callable(module=_COST_ESIMATOR_MODULE, callable_name=_COST_ESIMATOR_NAME)
    if _COST_ESIMATOR_NAME
    else _default_cost_estimator
)


# set up cost calculator function. This is called after job completes successfully.
# Default to a function that returns 0.
_COST_CALCULATOR_NAME = _cfg.get("cost_calculator", profile="callable_svc")
_COST_CALCULATOR_MODULE = (
    _cfg.get("cost_calculator_module", profile="callable_svc") or _CALLABLE_MODULE
)
CostCalculator: AppFunction = (
    _get_callable(module=_COST_CALCULATOR_MODULE, callable_name=_COST_CALCULATOR_NAME)
    if _COST_CALCULATOR_NAME
    else _default_cost_calculator
)
