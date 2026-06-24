from app.config import ADMIN_PASSWORD, ADMIN_USERNAME
from app.user_store import create_session, get_user, init_user


def login(username: str, password: str) -> dict | None:
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return None
    if not get_user(username):
        init_user(username)
    token = create_session(username)
    user = get_user(username)
    return {"token": token, "user": user}
