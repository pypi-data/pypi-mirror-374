from typing import Optional

from blacksheep import (
    Application,
    Response as BlackSheepResponse,
    Request as BlackSheepRequest,
)
from blacksheep import (
    get,
    put,
    post,
    patch,
    head,
    options,
    delete,
    route as all_route,
    Content,
    ws as websocket,
    WebSocket as BSWebSocket,
    StreamedContent,
)

from nestipy.types_ import CallableHandler, WebsocketHandler, MountHandler
from .http_adapter import HttpAdapter
from nestipy.common.http_ import Response, Websocket


class BlackSheepAdapter(HttpAdapter):
    def __init__(self):
        self.instance = Application()
        self.instance.on_start(self.on_startup)
        self.instance.on_stop(self.on_shutdown)

    def get_instance(self) -> Application:
        return self.instance

    def engine(self, args, *kwargs) -> None:
        pass

    def enable_cors(self) -> None:
        self.instance.use_cors(
            allow_methods="GET POST PUT DELETE OPTIONS",
            allow_origins="*",
            allow_headers="Content-Type",
            max_age=300,
        )

    def create_wichard(self, prefix: str = "/", name: str = "full_path") -> str:
        return f"/{prefix.strip('/')}" + "/{" + f"path:{name}" + "}"

    def use(self, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        # need to transform
        self.instance.middlewares.append(callback)

    def static(
            self, route: str, directory: str, name: str = None, option: dict = None
    ) -> None:
        # self.instance.serve_files()
        pass

    def get(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        get(route)(self._create_blacksheep_handler(callback, metadata))

    def post(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        post(route)(self._create_blacksheep_handler(callback, metadata))

    def put(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        put(route)(self._create_blacksheep_handler(callback, metadata))

    def delete(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        delete(route)(self._create_blacksheep_handler(callback, metadata))

    def options(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        options(route)(self._create_blacksheep_handler(callback, metadata))

    def head(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        head(route)(self._create_blacksheep_handler(callback, metadata))

    def patch(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        patch(route)(self._create_blacksheep_handler(callback, metadata))

    def all(self, route: str, callback: "CallableHandler", metadata: Optional[dict] = None) -> None:
        all_route(route,["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])(
            self._create_blacksheep_handler(callback, metadata)
        )

    def ws(self, route: str, callback: WebsocketHandler, metadata: Optional[dict] = None) -> None:
        websocket(route)(self._create_blacksheep_websocket_handler(callback, metadata))

    def mount(self, route: str, callback: MountHandler) -> None:
        self.instance.mount(route, callback)

    def _create_blacksheep_handler(self, callback: CallableHandler, metadata: Optional[dict] = None):
        # path = metadata['path']
        # params = RouteParamsExtractor.extract_params(path)
        async def blacksheep_handler(
                _bs_request: BlackSheepRequest,
        ) -> BlackSheepResponse:
            result: Response = await self.process_callback(callback, metadata)
            if result.is_stream():
                return BlackSheepResponse(
                    content=StreamedContent(
                        content_type=result.content_type().encode(),
                        data_provider=result.stream_content,
                    ),
                    headers=[(k.encode(), v.encode()) for k, v in result.headers()],
                    status=result.status_code() or 200,
                )
            return BlackSheepResponse(
                content=Content(
                    data=result.content(), content_type=result.content_type().encode()
                ),
                headers=[(k.encode(), v.encode()) for k, v in result.headers()],
                status=result.status_code() or 200,
            )

        return blacksheep_handler

    def _create_blacksheep_websocket_handler(
            self, callback: WebsocketHandler,
            _metadata: Optional[dict] = None
    ):
        async def blacksheep_websocket_handler(bsw: BSWebSocket):
            ws = Websocket(self.scope, self.receive, self.send)
            return await callback(ws)

        return blacksheep_websocket_handler
