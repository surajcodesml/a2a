import logging
from collections.abc import AsyncGenerator
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    FilePart, FileWithBytes, FileWithUri, Part, TaskState, TextPart, UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from google.adk import Runner
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PayStablAgentExecutor(AgentExecutor):
    """Runs the PayStabl ADK agent (exposes pay402_and_fetch via A2A)."""

    def __init__(self, runner: Runner):
        self.runner = runner

    def _run_agent(self, session_id: str, new_message: types.Content) -> AsyncGenerator[Event, None]:
        return self.runner.run_async(session_id=session_id, user_id="paystabl_agent", new_message=new_message)

    async def _process_request(self, new_message: types.Content, session_id: str, task_updater: TaskUpdater) -> None:
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id

        async for event in self._run_agent(session_id, new_message):
            if event.is_final_response():
                parts = convert_genai_parts_to_a2a(event.content.parts if event.content and event.content.parts else [])
                task_updater.add_artifact(parts)
                task_updater.complete()
                break
            if not event.get_function_calls():
                task_updater.update_status(
                    TaskState.working,
                    message=task_updater.new_agent_message(
                        convert_genai_parts_to_a2a(event.content.parts if event.content and event.content.parts else [])
                    ),
                )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        if not context.task_id or not context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not context.message:
            raise ValueError("RequestContext must have a message")

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            updater.submit()
        updater.start_work()

        await self._process_request(
            types.UserContent(parts=convert_a2a_parts_to_genai(context.message.parts)),
            context.context_id,
            updater,
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())

    async def _upsert_session(self, session_id: str):
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name, user_id="paystabl_agent", session_id=session_id
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, user_id="paystabl_agent", session_id=session_id
            )
        if session is None:
            raise RuntimeError(f"Failed to get or create session: {session_id}")
        return session


def convert_a2a_parts_to_genai(parts: list[Part]) -> list[types.Part]:
    return [convert_a2a_part_to_genai(p) for p in parts]

def convert_a2a_part_to_genai(part: Part) -> types.Part:
    root = part.root
    if isinstance(root, TextPart):
        return types.Part(text=root.text)
    if isinstance(root, FilePart):
        if isinstance(root.file, FileWithUri):
            return types.Part(file_data=types.FileData(file_uri=root.file.uri, mime_type=root.file.mimeType))
        if isinstance(root.file, FileWithBytes):
            return types.Part(inline_data=types.Blob(
                data=root.file.bytes.encode("utf-8"),
                mime_type=root.file.mimeType or "application/octet-stream"
            ))
    raise ValueError(f"Unsupported part type: {type(part)}")

def convert_genai_parts_to_a2a(parts: list[types.Part]) -> list[Part]:
    out: list[Part] = []
    for p in parts or []:
        if p.text:
            out.append(Part(root=TextPart(text=p.text)))
        elif p.file_data and p.file_data.file_uri:
            out.append(Part(root=FilePart(file=FileWithUri(uri=p.file_data.file_uri, mimeType=p.file_data.mime_type))))
        elif p.inline_data and p.inline_data.data:
            out.append(Part(root=FilePart(file=FileWithBytes(bytes=p.inline_data.data.decode("utf-8"),
                                                             mimeType=p.inline_data.mime_type))))
    return out
