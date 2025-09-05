import dataclasses
import inspect
import os
import sys
import traceback
import typing
from typing import Type, Union

from pydantic import BaseModel

from nestipy.common.exception import HttpException
from nestipy.common.exception.http import ExceptionDetail, RequestTrack, Traceback
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.common.http_ import Request, Response
from nestipy.common.utils import snakecase_to_camelcase
from nestipy.core.exception.processor import ExceptionFilterHandler
from nestipy.core.guards import GuardProcessor
from nestipy.core.interceptor import RequestInterceptor
from nestipy.core.middleware import MiddlewareExecutor
from nestipy.core.template import TemplateRendererProcessor
from nestipy.ioc import NestipyContainer
from nestipy.ioc import RequestContextContainer
from nestipy.openapi.openapi_docs.v3 import Operation, PathItem, Response as ApiResponse
from nestipy.types_ import NextFn, CallableHandler
from .route_explorer import RouteExplorer
from ..context.execution_context import ExecutionContext

if typing.TYPE_CHECKING:
    from ..adapter.http_adapter import HttpAdapter


def omit(d: dict, keys: set):
    return {k: v for k, v in d.items() if k not in keys}


class RouterProxy:
    def __init__(
        self,
        router: "HttpAdapter",
    ):
        self.router = router

    def apply_routes(self, modules: list[Union[Type, object]], prefix: str = ""):
        _prefix: Union[str | None] = (
            f"/{prefix.strip('/')}"
            if prefix is not None and prefix.strip() != ""
            else None
        )
        json_paths = {}
        json_schemas = {}
        list_routes = []
        for module_ref in modules:
            routes = RouteExplorer.explore(module_ref)
            list_routes = [
                *list_routes,
                *[omit(u, {"controller", "openapi", "schemas"}) for u in routes],
            ]
            for route in routes:
                path = (
                    f"{_prefix.rstrip('/')}/{route['path'].strip('/')}".rstrip("/")
                    if _prefix
                    else route["path"]
                )
                methods = route["request_method"]
                method_name = route["method_name"]
                controller = route["controller"]
                handler = self.create_request_handler(
                    self.router, module_ref, controller, method_name
                )
                for method in methods:
                    getattr(self.router, method.lower())(path, handler, route)
                    # OPEN API REGISTER
                    if path in json_paths:
                        route_path = json_paths[path]
                    else:
                        route_path = {}
                    if "responses" not in route["openapi"].keys():
                        route["openapi"]["responses"] = {200: ApiResponse()}
                    json_schemas = {**json_schemas, **route["schemas"]}
                    if "hidden" not in route["openapi"].keys():
                        route_path[method.lower()] = Operation(
                            **route["openapi"],
                            summary=snakecase_to_camelcase(method_name),
                        )
                        json_paths[path] = route_path
        paths = {}
        for path, op in json_paths.items():
            paths[path] = PathItem(**op)
        return paths, json_schemas, list_routes

    @classmethod
    def create_request_handler(
        cls,
        http_adapter: "HttpAdapter",
        module_ref: typing.Optional[Type] = None,
        controller: typing.Optional[Union[object, Type]] = None,
        method_name: typing.Optional[str] = None,
        custom_callback: typing.Optional[
            typing.Callable[["Request", "Response", NextFn], typing.Any]
        ] = None,
    ) -> CallableHandler:
        controller_method_handler = custom_callback or getattr(controller, method_name)
        _template_processor = TemplateRendererProcessor(http_adapter)
        context_container = RequestContextContainer.get_instance()
        container = NestipyContainer.get_instance()

        async def request_handler(req: "Request", res: "Response", next_fn: NextFn):
            execution_context = ExecutionContext(
                http_adapter,
                custom_callback or module_ref,
                custom_callback or controller,
                controller_method_handler,
                req,
                res,
            )
            # setup container for query params, route params, request, response, session, etc..
            context_container.set_execution_context(execution_context)
            handler_response: Response
            try:

                async def next_fn_interceptor(ex: typing.Any = None):
                    if ex is not None:
                        return await cls._ensure_response(res, await next_fn(ex))
                    if custom_callback:
                        callback_res = custom_callback(req, res, next_fn)
                        if inspect.isawaitable(callback_res):
                            return await callback_res
                        else:
                            return callback_res
                    return await container.get(controller, method_name)

                async def next_fn_middleware(ex: typing.Any = None):
                    if ex is not None:
                        raise ex
                    g_processor: GuardProcessor = await container.get(GuardProcessor)
                    passed = await g_processor.process(execution_context)
                    if not passed[0]:
                        raise HttpException(
                            HttpStatus.UNAUTHORIZED,
                            HttpStatusMessages.UNAUTHORIZED,
                            details=f"Not authorized from guard {passed[1]}",
                        )

                    interceptor: RequestInterceptor = await container.get(
                        RequestInterceptor
                    )
                    resp = await interceptor.intercept(
                        execution_context, next_fn_interceptor
                    )
                    #  execute Interceptor by using middleware execution as next_handler
                    if resp is None:
                        raise HttpException(
                            HttpStatus.BAD_REQUEST,
                            "Handler not called because of interceptor: Invalid Request",
                        )
                    return resp

                # Call middleware before all
                result = await MiddlewareExecutor(
                    req, res, next_fn_middleware
                ).execute()

                # process template rendering

                if _template_processor.can_process(controller_method_handler, result):
                    result = await res.html(_template_processor.render())
                # transform result to response
                handler_response = await cls._ensure_response(res, result)

            except Exception as e:
                handler_response = await cls.handle_exception(
                    e, execution_context, next_fn
                )
            finally:
                #  reset request context container
                context_container.destroy()
            return handler_response

        return request_handler

    @classmethod
    async def _ensure_response(
        cls, res: "Response", result: Union["Response", str, dict, list]
    ) -> "Response":
        if isinstance(result, (str, int, float)):
            return await res.send(content=str(result))
        elif isinstance(result, (list, dict)):
            return await res.json(content=result)
        elif dataclasses.is_dataclass(result):
            return await res.json(
                content=dataclasses.asdict(typing.cast(dataclasses.dataclass, result)),
            )
        elif isinstance(result, BaseModel):
            return await res.json(content=result.model_dump(mode="json"))
        elif isinstance(result, Response):
            return result
        else:
            return await res.json(
                content={"error": "Unknown response format"}, status_code=403
            )

    @classmethod
    def get_center_elements(cls, lst: list, p: int, m: int):
        n = len(lst)
        size = (m * 2) + 1
        if n < size:
            return lst, 1
        start = max(0, p - m - 1)
        end = min(n, p + m + 1)

        return lst[start:end], start + 1

    @classmethod
    def get_code_context(cls, filename, lineno, n):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
            elements, start_line = cls.get_center_elements(lines, lineno, n)
            return "".join(elements), start_line
        except Exception as e:
            return f"Could not read file {filename}: {str(e)}"

    @classmethod
    async def render_not_found(
        cls, _req: "Request", _res: "Response", _next_fn: "NextFn"
    ) -> Response:
        raise HttpException(
            HttpStatus.NOT_FOUND,
            HttpStatusMessages.NOT_FOUND,
            "Sorry, but the page you are looking for has not been found or temporarily unavailable.",
        )

    @classmethod
    async def handle_exception(
        cls, ex: Exception, execution_context: ExecutionContext, next_fn: NextFn
    ):
        tb = traceback.format_exc()
        if not isinstance(ex, HttpException):
            ex = HttpException(HttpStatus.INTERNAL_SERVER_ERROR, str(ex), str(tb))
        track_b = cls.get_full_traceback_details(
            execution_context.get_request(),
            ex.message,
            os.getcwd(),
        )
        ex.track_back = track_b
        exception_handler = await NestipyContainer.get_instance().get(
            ExceptionFilterHandler
        )
        result = await exception_handler.catch(ex, execution_context)
        if result:
            handler_response = await cls._ensure_response(
                execution_context.get_response(), result
            )
        else:
            handler_response = await cls._ensure_response(
                execution_context.get_response(), await next_fn(ex)
            )
        return handler_response

    @classmethod
    def get_full_traceback_details(
        cls, req: Request, exception: typing.Any, file_path: str
    ):
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback_details = []

        # Extracting traceback details
        tb = exc_tb
        while tb is not None:
            filename: str = tb.tb_frame.f_code.co_filename
            code, start = cls.get_code_context(
                tb.tb_frame.f_code.co_filename, tb.tb_lineno, 9
            )
            frame_info = Traceback(
                filename=f"{filename.replace(file_path, '').strip('/')}",
                lineno=tb.tb_lineno,
                name=tb.tb_frame.f_code.co_name,
                code=code,
                start_line_number=start,
                is_package=not filename.startswith(file_path),
            )
            traceback_details.append(frame_info)
            tb = tb.tb_next
        traceback_details.reverse()
        return ExceptionDetail(
            exception=exception,
            type=exc_type.__name__,
            root=file_path,
            traceback=traceback_details,
            request=RequestTrack(method=req.method, host=req.path),
            message=getattr(exc_value, "details", None) or str(exc_value),
        )
