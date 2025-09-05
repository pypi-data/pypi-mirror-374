from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from lymo.router import match_route
from lymo.http_requests import HttpRequest
from lymo.http_responses import TemplateResponse


if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import APIGatewayProxyEventV1
    from lymo.http_responses import HttpResponse
    from lymo.app import App


def strip_base_path(resource: str, path: str) -> str:
    base = resource.split("/{", 1)[0]
    if path.startswith(base):
        trimmed = path[len(base) :]
    else:
        trimmed = path
    return trimmed or "/"


def http_handler(
    event: APIGatewayProxyEventV1,
    context: Context,
    app: App,
) -> HttpResponse:
    request = HttpRequest(
        event=event,
        context=context,
        template_env=app.template_env,
        resources=app.resources,
    )
    try:
        path = strip_base_path(event.get("resource", ""), event.get("path", ""))
        handler, params = match_route(path, event["httpMethod"])
        if handler:
            request.path_params = params
            return handler(request)

        return TemplateResponse(
            request=request,
            template="404.html",
            context={},
            status_code=404,
        )

    except Exception as e:
        if app.logger:
            app.logger.error(f"Error in lambda_handler: {e}")
        trace = traceback.format_exc()
        return TemplateResponse(
            request=request,
            template="500.html",
            context={"error": e, "traceback": trace},
            status_code=404,
        )
