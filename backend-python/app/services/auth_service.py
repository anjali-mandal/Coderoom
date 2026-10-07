from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.db.postgres import get_db, new_id


async def register_user(name: str, email: str, password: str) -> dict:
    pool = get_db()
    normalized_email = email.strip().lower()
    async with pool.acquire() as connection:
        existing = await connection.fetchval("SELECT id FROM users WHERE email = $1", normalized_email)
        if existing:
            raise ValueError("Email already registered")
        user_doc = await connection.fetchrow(
            """INSERT INTO users (id, name, email, password)
            VALUES ($1, $2, $3, $4) RETURNING id, name, email""",
            new_id(), name.strip(), normalized_email, hash_password(password)
        )

    user = {"id": str(user_doc["id"]), "name": user_doc["name"], "email": user_doc["email"]}
    token = create_access_token({"userId": user["id"], "email": user["email"]})

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


async def login_user(email: str, password: str) -> dict:
    pool = get_db()
    async with pool.acquire() as connection:
        user_doc = await connection.fetchrow(
            "SELECT id, name, email, password FROM users WHERE email = $1",
            email.strip().lower(),
        )
    if not user_doc or not verify_password(password, user_doc["password"]):
        raise ValueError("Invalid email or password")

    user = {"id": str(user_doc["id"]), "name": user_doc["name"], "email": user_doc["email"]}
    token = create_access_token({"userId": user["id"], "email": user["email"]})

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


def verify_token(token: str) -> dict:
    try:
        return decode_token(token)
    except Exception as exc:
        raise ValueError("Invalid or expired token") from exc


async def get_user_by_id(user_id: str) -> dict | None:
    pool = get_db()
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "SELECT id, name, email FROM users WHERE id = $1::uuid", user_id
        )
    if not row:
        return None
    return {"id": str(row["id"]), "name": row["name"], "email": row["email"]}


