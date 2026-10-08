from uuid import UUID

from app.db.postgres import get_db, new_id


async def create_project(project_name: str, user_id: str) -> dict:
    pool = get_db()
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            """INSERT INTO projects (id, owner_id, name)
            VALUES ($1, $2::uuid, $3) RETURNING id, name, code, review""",
            new_id(), user_id, project_name.strip()
        )
        await connection.execute(
            "INSERT INTO project_members (project_id, user_id) VALUES ($1, $2::uuid)",
            row["id"], user_id,
        )
    return {"_id": str(row["id"]), "name": row["name"], "code": row["code"], "review": row["review"]}


async def get_all_projects(user_id: str) -> list[dict]:
    pool = get_db()
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """SELECT p.id, p.name, p.code, p.review FROM projects p
            INNER JOIN project_members pm ON pm.project_id = p.id
            WHERE pm.user_id = $1::uuid ORDER BY p.created_at DESC""", user_id
        )
    return [{"_id": str(row["id"]), "name": row["name"], "code": row["code"], "review": row["review"]} for row in rows]


async def add_project_member(project_id: str, owner_id: str, member_email: str) -> dict:
    try:
        project_uuid = UUID(project_id)
        owner_uuid = UUID(owner_id)
    except ValueError as exc:
        raise ValueError("Invalid project or user id") from exc

    email = member_email.strip().lower()
    if not email:
        raise ValueError("Member email is required")

    pool = get_db()
    async with pool.acquire() as connection:
        project = await connection.fetchval(
            "SELECT id FROM projects WHERE id = $1 AND owner_id = $2",
            project_uuid, owner_uuid,
        )
        if not project:
            raise ValueError("Only the project owner can add members")

        member = await connection.fetchrow(
            "SELECT id, name, email FROM users WHERE email = $1",
            email,
        )
        if not member:
            raise ValueError("No account found for this email")
        if member["id"] == owner_uuid:
            raise ValueError("You already own this project")

        await connection.execute(
            """INSERT INTO project_members (project_id, user_id) VALUES ($1, $2)
            ON CONFLICT (project_id, user_id) DO NOTHING""",
            project_uuid, member["id"],
        )
    return {"id": str(member["id"]), "name": member["name"], "email": member["email"]}


async def update_project_code(project_id: str, code: str) -> None:
    pool = get_db()
    async with pool.acquire() as connection:
        await connection.execute("UPDATE projects SET code = $1 WHERE id = $2::uuid", code, project_id)
