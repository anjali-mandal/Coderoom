from uuid import UUID, uuid4

import asyncpg

from app.core.config import settings


_pool: asyncpg.Pool | None = None


async def connect_to_postgres() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=15,
        )
        await _pool.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(320) NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY,
                owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(160) NOT NULL,
                code TEXT NOT NULL DEFAULT '',
                review TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS messages (
                id BIGSERIAL PRIMARY KEY,
                project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                text TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS project_members (
                project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (project_id, user_id)
            );
            CREATE INDEX IF NOT EXISTS projects_owner_id_idx ON projects(owner_id);
            CREATE INDEX IF NOT EXISTS messages_project_id_idx ON messages(project_id, created_at);
            CREATE INDEX IF NOT EXISTS project_members_user_id_idx ON project_members(user_id);
            INSERT INTO project_members (project_id, user_id)
            SELECT id, owner_id FROM projects
            ON CONFLICT (project_id, user_id) DO NOTHING;
            """
        )
    return _pool


def get_db() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("PostgreSQL is not connected")
    return _pool


async def close_postgres() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def new_id() -> UUID:
    return uuid4()