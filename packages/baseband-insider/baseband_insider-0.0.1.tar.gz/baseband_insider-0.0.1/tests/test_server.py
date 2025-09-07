from __future__ import annotations

import asyncio
import json
from typing import List

import websockets

from baseband_insider import Agent, Section, Text, serve_in_background


class _MiniAgent(Agent):
    def execute(self, context) -> None:  # context provided by server
        sec = Section(id="test")
        head = Text(parent=sec)
        head.append("hi")


async def _collect_events(limit: int = 2) -> List[dict]:
    events: List[dict] = []
    uri = "ws://127.0.0.1:4680/v1/stream"
    async with websockets.connect(uri) as ws:
        while len(events) < limit:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            events.append(json.loads(msg))
    return events


def test_server_streams_agent_events() -> None:
    port = 4690
    stop, ready = serve_in_background(lambda: _MiniAgent(), port=port)
    assert ready.wait(timeout=2)

    try:

        async def _collect_on_port() -> list[dict]:
            events: list[dict] = []
            uri = f"ws://127.0.0.1:{port}/v1/stream"
            async with websockets.connect(uri) as ws:
                # Receive meta first
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                meta_evt = json.loads(msg)
                events.append(meta_evt)
                # Send control message with prompt to start agent execution
                await ws.send(
                    json.dumps(
                        {
                            "type": "user_prompt",
                            "threadId": "thread-1",
                            "messageId": "message-1",
                            "promptText": "hello",
                            "timestamp": 0,
                        }
                    )
                )
                # Collect subsequent events
                while len(events) < 3:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2)
                    events.append(json.loads(msg))
            return events

        events = asyncio.run(_collect_on_port())
    finally:
        stop()

    kinds = [e.get("data", {}).get("type") for e in events]
    assert "section" in kinds
    assert "text" in kinds


def test_request_ids_differ_per_connection() -> None:
    # Start one server and open two connections to it
    port = 4692
    stop, ready = serve_in_background(lambda: _MiniAgent(), port=port)
    assert ready.wait(timeout=2)

    async def _first_meta_event() -> str:
        uri = f"ws://127.0.0.1:{port}/v1/stream"
        async with websockets.connect(uri) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            evt = json.loads(msg)
            assert evt["event_type"] == "meta_event"
            return evt["request_id"]

    try:

        async def _both() -> tuple[str, str]:
            rid_a, rid_b = await asyncio.gather(_first_meta_event(), _first_meta_event())
            return rid_a, rid_b

        rid1, rid2 = asyncio.run(_both())
    finally:
        stop()

    assert rid1 != rid2
