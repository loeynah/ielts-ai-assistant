from app.user_store import create_session, get_user, register_user, verify_user_password


def login(username: str, password: str) -> dict | None:
    username = username.strip()
    if not verify_user_password(username, password):
        return None
    token = create_session(username)
    user = get_user(username)
    return {"token": token, "user": user}


def register(username: str, password: str) -> dict:
    user = register_user(username.strip(), password)
    token = create_session(user["username"])
    return {"token": token, "user": user}
