import sys
from collections.abc import Generator
from typing import Any

from gevent.os import tp_read
from pydantic import TypeAdapter

from dify_plugin.core.entities.plugin.io import (
    PluginInStream,
    PluginInStreamEvent,
)
from dify_plugin.core.server.__base.request_reader import RequestReader
from dify_plugin.core.server.stdio.response_writer import StdioResponseWriter


class StdioRequestReader(RequestReader):
    def __init__(self):
        super().__init__()

    def _read_async(self) -> bytes:
        # read data from stdin using tp_read in 64KB chunks.
        # the OS buffer for stdin is usually 64KB, so using a larger value doesn't make sense.
        return tp_read(sys.stdin.fileno(), 65536)

    def _read_stream(self) -> Generator[PluginInStream, None, None]:
        buffer = b""
        while True:
            data = self._read_async()
            if not data:
                continue

            buffer += data

            # if no b"\n" is in data, skip to the next iteration
            if data.find(b"\n") == -1:
                continue

            # process line by line and keep the last line if it is not complete
            lines = buffer.split(b"\n")
            buffer = lines[-1]

            lines = lines[:-1]
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = TypeAdapter(dict[str, Any]).validate_json(line)
                    yield PluginInStream(
                        session_id=data["session_id"],
                        conversation_id=data.get("conversation_id"),
                        message_id=data.get("message_id"),
                        app_id=data.get("app_id"),
                        endpoint_id=data.get("endpoint_id"),
                        event=PluginInStreamEvent.value_of(data["event"]),
                        data=data["data"],
                        context=data.get("context"),
                        reader=self,
                        writer=StdioResponseWriter(),
                    )
                except Exception as e:
                    StdioResponseWriter().error(data={"error": str(e)})
