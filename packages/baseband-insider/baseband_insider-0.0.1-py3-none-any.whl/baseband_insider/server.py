from __future__ import annotations

import asyncio
import contextlib
import inspect
import json
import threading
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from typing import Awaitable, Callable, Dict, Optional, Tuple

import websockets
from websockets.datastructures import Headers
from websockets.server import WebSocketServerProtocol

from .context import EventStack, event_stack
from .protocol import MetaEvent, StatusChangeEvent, StatusContext, serialize_event
from .utils import now_ms


async def _process_http_request(
    path: str, headers: Headers
) -> Optional[Tuple[HTTPStatus, Dict[str, str], bytes]]:
    """Handle HTTP requests for non-websocket endpoints."""
    if path == "/health":
        return HTTPStatus.OK, {"Content-Type": "application/json"}, b'{"status":"ok"}'

    # Let /v1/stream be handled by the WebSocket handler
    if path == "/v1/stream":
        return None

    # For any other path, return 404
    return HTTPStatus.NOT_FOUND, {}, b'{"error":"Not Found"}'


@dataclass
class ThreadContext:
    thread_id: str
    message_id: str
    prompt_text: str
    timestamp: int


class Agent:
    def __init__(self) -> None:
        self._stack: Optional[EventStack] = None  # set during _run
        self.request_id: str = uuid.uuid4().hex

    def execute(
        self, context: ThreadContext
    ) -> Optional[Awaitable[None]]:  # Override in subclasses (can be sync or async)
        raise NotImplementedError

    def _run(self, context: ThreadContext) -> None:
        """Synchronous _run for backward compatibility."""
        with event_stack() as stack:
            self._stack = stack
            print(f"[agent {self.request_id}] start")
            self.execute(context)
            print(f"[agent {self.request_id}] finished")

    async def _run_async(self, context: ThreadContext) -> None:
        """Asynchronous _run for async execute methods."""
        with event_stack() as stack:
            self._stack = stack
            print(f"[agent {self.request_id}] start")
            result = self.execute(context)
            if inspect.isawaitable(result):
                await result
            print(f"[agent {self.request_id}] finished")

    def is_async(self) -> bool:
        """Check if the agent's execute method is async."""
        return inspect.iscoroutinefunction(self.execute)


async def _websocket_handler(
    websocket: "WebSocketServerProtocol", path: str, agent_factory: Callable[[], Agent]
) -> None:
    """Handle websocket connections only for /v1/stream path."""
    if path != "/v1/stream":
        await websocket.close(code=1000, reason="Websocket endpoint not found")
        return

    await _connection_handler(websocket, agent_factory)


async def _connection_handler(
    websocket: "WebSocketServerProtocol", agent_factory: Callable[[], Agent]
) -> None:
    agent: Agent = agent_factory()

    # Send a meta event with request id first
    meta: MetaEvent = MetaEvent(timestamp=now_ms(), request_id=agent.request_id)
    await websocket.send(serialize_event(meta))

    # Wait for initial control message carrying the user's prompt
    # Expected shape (from gateway):
    # {
    #   "type": "user_prompt",
    #   "threadId": string,
    #   "messageId": string,
    #   "promptText": string,
    #   "timestamp": number
    # }
    ctx: Optional[ThreadContext] = None
    while ctx is None:
        raw = await websocket.recv()
        try:
            data = json.loads(raw)
        except Exception:
            # Ignore non-JSON messages
            continue
        if not isinstance(data, dict):
            continue
        if data.get("type") != "user_prompt":
            continue
        thread_id = str(data.get("threadId", ""))
        message_id = str(data.get("messageId", ""))
        prompt_text = str(data.get("promptText", ""))
        timestamp = int(data.get("timestamp", 0))
        if not thread_id or not message_id or not prompt_text:
            # Incomplete; keep waiting
            continue
        ctx = ThreadContext(
            thread_id=thread_id,
            message_id=message_id,
            prompt_text=prompt_text,
            timestamp=timestamp,
        )

    # Choose execution strategy based on whether the agent is async
    agent_task: "asyncio.Task[None]"
    if agent.is_async():
        # For async agents, run directly in the event loop for better streaming
        agent_task = asyncio.create_task(agent._run_async(ctx))
    else:
        # For sync agents, run in a worker thread to avoid blocking
        agent_task = asyncio.create_task(asyncio.to_thread(agent._run, ctx))

    try:
        while True:
            # Wait until the agent has initialized its stack
            stack_ref = agent._stack
            if stack_ref is not None:
                # Pop and stream any pending events in FIFO order
                while stack_ref.events:
                    payload = stack_ref.events.pop(0)
                    await websocket.send(serialize_event(payload))

            if agent_task.done():
                # If the agent task is complete, decide final status and exit
                exc: Optional[BaseException] = agent_task.exception()
                if exc is None:
                    # Success: emit finished status (only after draining pending events)
                    stack_after = agent._stack
                    if stack_after is None or not stack_after.events:
                        await websocket.send(
                            serialize_event(
                                StatusChangeEvent(target_status="finished")
                            )
                        )
                        break
                else:
                    # Failure: emit failed status with error context
                    await websocket.send(
                        serialize_event(
                            StatusChangeEvent(
                                target_status="failed",
                                context=StatusContext(error=str(exc)),
                            )
                        )
                    )
                    break

            # For async agents, use a shorter sleep for better responsiveness
            sleep_time: float = 0.01 if agent.is_async() else 0.05
            await asyncio.sleep(sleep_time)
    except Exception as e:
        # Any unexpected exception: emit failed status with context
        with contextlib.suppress(Exception):
            await websocket.send(
                serialize_event(
                    StatusChangeEvent(
                        target_status="failed",
                        context=StatusContext(error=str(e)),
                    )
                )
            )
    finally:
        if not agent_task.done():
            agent_task.cancel()
            with contextlib.suppress(Exception):
                await agent_task


def serve_in_background(
    agent_factory: Callable[[], Agent], host: str = "127.0.0.1", port: int = 4680
) -> Tuple[Callable[[], None], threading.Event]:
    """Start the websocket server in a background thread.

    Returns a tuple of (stop, ready) where stop() will shut the server down,
    and ready is a threading.Event set when the server is accepting connections.
    """

    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    stop_event: asyncio.Event = asyncio.Event()
    ready: threading.Event = threading.Event()

    async def _main() -> None:
        async with websockets.serve(
            lambda ws, path: _websocket_handler(ws, path, agent_factory),
            host,
            port,
            process_request=_process_http_request,
        ):
            ready.set()
            await stop_event.wait()

    def _run() -> None:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_main())

    thread: threading.Thread = threading.Thread(target=_run, name="baseband-ws-server", daemon=True)
    thread.start()

    def stop() -> None:
        def _stop() -> Awaitable[None]:
            stop_event.set()
            return asyncio.sleep(0)

        asyncio.run_coroutine_threadsafe(_stop(), loop).result(timeout=2)
        thread.join(timeout=2)

    return stop, ready
