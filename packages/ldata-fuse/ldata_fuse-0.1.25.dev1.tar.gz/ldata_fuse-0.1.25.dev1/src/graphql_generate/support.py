import json
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import (
    Callable,
    Coroutine,
    Generic,
    Literal,
    NotRequired,
    TypedDict,
    TypeVar,
)

from aiohttp import ClientSession, ClientWebSocketResponse, WSMessage, WSMsgType
from aiohttp.http import SERVER_SOFTWARE
from latch_data_validation.data_validation import (
    JsonObject,
    JsonValue,
    untraced_validate,
)
from opentelemetry.trace import get_tracer

tracer = get_tracer(__name__)

RT = TypeVar("RT")


class GqlErrorExtensionException(TypedDict):
    errcode: str


class GqlErrorExtension(TypedDict):
    exception: GqlErrorExtensionException


class GqlErrorLocation(TypedDict):
    line: int
    column: int


class GqlErrorPayload(TypedDict):
    errcode: str
    extensions: list[GqlErrorExtension]
    message: str
    locations: list[GqlErrorLocation]
    path: list[str]
    stack: list[str]


class GqlError(RuntimeError):
    def __init__(self, errors: list[GqlErrorPayload]):
        self.errors = errors

        super().__init__("\n".join(json.dumps(x) for x in self.errors))


# todo(maximsmol): add the git hash
user_agent = f"LDataFUSE/0.1.0 {SERVER_SOFTWARE}"


class GqlConnectionAckMessage(TypedDict):
    type: Literal["connection_ack"]
    payload: NotRequired[dict[str, object]]


class GqlPingMessage(TypedDict):
    type: Literal["ping"]
    payload: NotRequired[dict[str, object]]


class GqlPongMessage(TypedDict):
    type: Literal["pong"]
    payload: NotRequired[dict[str, object]]


class GqlNextMessagePayload(TypedDict):
    data: JsonValue


class GqlNextMessage(TypedDict):
    type: Literal["next"]
    id: str
    payload: GqlNextMessagePayload


class GqlErrorMessage(TypedDict):
    type: Literal["error"]
    id: str
    payload: list[GqlErrorPayload]


class GqlCompleteMessage(TypedDict):
    type: Literal["complete"]
    id: str


@dataclass
class GqlSubscriptionData(Generic[RT]):
    data: RT


@dataclass
class GqlSubscriptionErrors:
    errors: list[GqlErrorPayload]


class WebSocketClosedException(Exception):
    def __init__(self, message: WSMessage):
        self.message = message

        super().__init__(f"{repr(message.type)}: {message.data} ({message.extra})")


class WebSocketErrorMessage(RuntimeError):
    def __init__(self, message: WSMessage):
        self.message = message

        super().__init__(f"{repr(message.type.name)}: {message.data} ({message.extra})")


@dataclass
class GqlWebSocketContext:
    # https://github.com/enisdenjo/graphql-ws/blob/50d5a512d0d7252d41c079e6716b884a191b1ddc/PROTOCOL.md
    sock: ClientWebSocketResponse

    _op_cb: dict[str, tuple[type, Callable]] = field(init=False, default_factory=dict)

    async def receive(self, *, timeout: float | None = None) -> JsonObject:
        data_msg = await self.sock.receive(timeout=timeout)
        if data_msg.type == WSMsgType.CLOSING:
            raise WebSocketClosedException(data_msg)

        if data_msg.type == WSMsgType.CLOSE:
            if data_msg.data is None or data_msg.data in 1000:
                raise WebSocketClosedException(data_msg)
            raise WebSocketErrorMessage(data_msg)

        return data_msg.json()

    async def connection_init(
        self, *, authorization: str, timeout: float | None = None
    ):
        await self.sock.send_json(
            {"type": "connection_init", "payload": {"authorization": authorization}}
        )

        msg = await self.receive(timeout=timeout)
        return untraced_validate(msg, GqlConnectionAckMessage).get("payload")

    async def ping(self):
        await self.sock.send_json({"type": "ping"})

    async def pong(self):
        await self.sock.send_json({"type": "pong"})

    async def subscribe(
        self,
        *,
        operation_id: str,
        query_str: str,
        variables: dict[str, object],
        result_type: type[RT],
        callback: Callable[
            [GqlSubscriptionData[RT] | GqlSubscriptionErrors],
            Coroutine[object, object, object],
        ],
    ):
        await self.sock.send_json(
            {
                "type": "subscribe",
                "id": operation_id,
                "payload": {"query": query_str, "variables": variables},
            }
        )
        self._op_cb[operation_id] = (result_type, callback)

    async def poll(self, *, timeout: float | None = None):
        data = await self.receive(timeout=timeout)

        if data["type"] == "pong":
            return untraced_validate(data, GqlPongMessage)
        elif data["type"] == "ping":
            msg = untraced_validate(data, GqlPingMessage)
            await self.pong()
            return msg
        elif data["type"] == "next":
            msg = untraced_validate(data, GqlNextMessage)

            op_data = self._op_cb.get(msg["id"])
            if op_data is not None:
                await op_data[1](
                    GqlSubscriptionData(
                        untraced_validate(msg["payload"]["data"], op_data[0])
                    )
                )

            return msg
        elif data["type"] == "error":
            msg = untraced_validate(data, GqlErrorMessage)

            op_data = self._op_cb.get(msg["id"])
            if op_data is not None:
                await op_data[1](GqlSubscriptionErrors(msg["payload"]))

            return msg
        elif data["type"] == "complete":
            msg = untraced_validate(data, GqlCompleteMessage)

            if msg["id"] in self._op_cb:
                del self._op_cb[msg["id"]]

            return msg

        raise RuntimeError(
            f"unknown GraphQL WebSocket message type: {repr(data['type'])}"
        )


@dataclass
class GqlContext:
    sess: ClientSession
    url: str

    @asynccontextmanager
    async def ws_connect(self):
        async with self.sess.ws_connect(
            self.url,
            protocols=["graphql-transport-ws"],
            headers={"User-Agent": user_agent},
            max_msg_size=0,
        ) as conn:
            ws = GqlWebSocketContext(conn)
            await ws.connection_init(authorization=self.sess.headers["Authorization"])
            yield ws

    async def query(
        self,
        *,
        query_str: str,
        variables: dict[str, object] | None = None,
        result_type: type[RT],
    ) -> RT:
        data = {
            "query": query_str,
        } | ({"variables": variables} if variables is not None else {})

        res = await self.sess.post(
            self.url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json", "User-Agent": user_agent},
        )

        data = await res.json()
        if "errors" in data:
            raise GqlError(data["errors"])

        return untraced_validate(data["data"], result_type)
