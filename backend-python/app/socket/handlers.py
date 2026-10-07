from uuid import UUID
from urllib.parse import parse_qs

import socketio

from app.db.postgres import get_db
from app.services.ai_service import get_review
from app.services.auth_service import verify_token
from app.services.project_service import update_project_code


def _uuid(value: str | None) -> UUID | None:
    try:
        return UUID(value) if value else None
    except ValueError:
        return None


def register_socket_handlers(sio: socketio.AsyncServer) -> None:
    @sio.event
    async def connect(sid, environ, auth):
        token = auth.get("token") if isinstance(auth, dict) else auth
        if not token:
            return False

        try:
            decoded = verify_token(token)
        except ValueError:
            return False

        project_id = parse_qs(environ.get("QUERY_STRING", "")).get("project", [None])[0]
        project_uuid = _uuid(project_id)
        user_uuid = _uuid(decoded.get("userId"))
        if not project_id or not project_uuid or not user_uuid:
            return False

        pool = get_db()
        async with pool.acquire() as connection:
            project_exists = await connection.fetchval(
                """SELECT EXISTS(
                    SELECT 1 FROM project_members WHERE project_id = $1 AND user_id = $2
                )""",
                project_uuid,
                user_uuid,
            )
        if not project_exists:
            return False

        await sio.save_session(sid, {
            "user_id": str(user_uuid),
            "user_email": decoded.get("email"),
            "project_id": project_id,
        })
        await sio.enter_room(sid, project_id)
        return True

    @sio.event
    async def disconnect(sid):
        return None

    @sio.on("chat-history")
    async def chat_history(sid):
        try:
            session = await sio.get_session(sid)
            project_uuid = _uuid(session.get("project_id") if session else None)
            if not project_uuid:
                await sio.emit("error", "Invalid project id", to=sid)
                return

            pool = get_db()
            async with pool.acquire() as connection:
                rows = await connection.fetch(
                    """SELECT id, text, user_id, created_at FROM messages
                    WHERE project_id = $1 ORDER BY created_at ASC LIMIT 1000""",
                    project_uuid,
                )
            payload = [{
                "_id": str(row["id"]),
                "text": row["text"],
                "user": str(row["user_id"]),
                "created_at": row["created_at"].isoformat(),
            } for row in rows]
            await sio.emit("chat-history", payload, to=sid)
        except Exception as exc:
            await sio.emit("error", f"Failed to get chat history: {exc}", to=sid)

    @sio.on("get-project-code")
    async def get_project_code(sid):
        try:
            session = await sio.get_session(sid)
            project_uuid = _uuid(session.get("project_id") if session else None)
            if not project_uuid:
                await sio.emit("error", "Invalid project id", to=sid)
                return
            pool = get_db()
            async with pool.acquire() as connection:
                code = await connection.fetchval("SELECT code FROM projects WHERE id = $1", project_uuid)
            await sio.emit("project-code", code or "", to=sid)
        except Exception as exc:
            await sio.emit("error", f"Failed to get project code: {exc}", to=sid)

    @sio.on("chat-message")
    async def chat_message(sid, message):
        try:
            session = await sio.get_session(sid)
            project_id = session.get("project_id") if session else None
            project_uuid = _uuid(project_id)
            user_uuid = _uuid(session.get("user_id") if session else None)
            if not project_uuid or not user_uuid or not isinstance(message, str) or not message.strip():
                await sio.emit("error", "Invalid message", to=sid)
                return

            text = message.strip()
            pool = get_db()
            async with pool.acquire() as connection:
                await connection.execute(
                    "INSERT INTO messages (project_id, user_id, text) VALUES ($1, $2, $3)",
                    project_uuid, user_uuid, text,
                )
            await sio.emit(
                "chat-message",
                {"text": text, "userId": str(user_uuid)},
                room=project_id,
                skip_sid=sid,
            )
        except Exception as exc:
            await sio.emit("error", f"Failed to send message: {exc}", to=sid)

    @sio.on("code-change")
    async def code_change(sid, code):
        if not isinstance(code, str):
            await sio.emit("error", "Invalid code", to=sid)
            return
        try:
            session = await sio.get_session(sid)
            project_id = session.get("project_id") if session else None
            if not project_id:
                await sio.emit("error", "Invalid project id", to=sid)
                return
            await update_project_code(project_id, code)
            await sio.emit("code-change", code, room=project_id, skip_sid=sid)
        except Exception as exc:
            await sio.emit("error", f"Failed to update code: {exc}", to=sid)

    @sio.on("get-review")
    async def get_review_event(sid, code):
        try:
            session = await sio.get_session(sid)
            if not session or not isinstance(code, str):
                await sio.emit("review-error", "Invalid review request", to=sid)
                return
            review = await get_review(code)
            await sio.emit("code-review", review, to=sid)
        except Exception as exc:
            await sio.emit("review-error", str(exc), to=sid)