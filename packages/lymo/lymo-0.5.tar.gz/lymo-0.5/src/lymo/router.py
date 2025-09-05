from __future__ import annotations

import importlib
import json
import pkgutil
import re

APP_ROUTES = []


def route(path_pattern: str, method: str):
    method = method.upper()
    normalized_pattern = path_pattern.strip("/")  # ← define this here

    def wrapper(func):
        regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", normalized_pattern)
        APP_ROUTES.append((method, re.compile(f"^{regex}$"), func))
        return func

    return wrapper


def match_route(path: str, method: str):
    normalized = path.strip("/")
    for route_method, route_pattern, handler in APP_ROUTES:
        if method == route_method:
            m = route_pattern.match(normalized)
            if m:
                return handler, m.groupdict()
    return None, {}


def http_not_found(event, context):
    return {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}


def load_routes(package):
    """
    Dynamically import all submodules of the given package
    so that any @route() decorators in them get registered.

    Usage:
        load_routes(routes)
    """
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_name = f"{package.__name__}.{module_name}"
        importlib.import_module(full_name)
