import pytest
from fastapi.testclient import TestClient

from src.main import app



@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_user(
    client: TestClient,
    username: str = "alice",
    email: str = "alice@example.com",
    password: str = "123456",
):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(
    client: TestClient,
    email: str = "alice@example.com",
    password: str = "123456",
):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def test_user_crud_flow(client: TestClient) -> None:
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []

    response = client.post(
        "/users/",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["username"] == "john"
    assert created_user["email"] == "john@example.com"
    assert "id" in created_user
    assert "password" not in created_user

    user_id = created_user["id"]

    response = client.post(
        "/users/",
        json={
            "username": "john2",
            "email": "john@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

    response = client.put(
        f"/users/{user_id}",
        json={"email": "newjohn@example.com"},
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == "newjohn@example.com"
    assert updated_user["username"] == "john"

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user["id"] == user_id

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_user_batch_routes(client: TestClient) -> None:
    response = client.post(
        "/users/many",
        json=[
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "123456",
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "123456",
            },
        ],
    )
    assert response.status_code == 200
    created_users = response.json()
    assert len(created_users) == 2
    assert created_users[0]["id"] == 1
    assert created_users[1]["id"] == 2

    response = client.get("/users/by-ids", params=[("user_ids", 1), ("user_ids", 2), ("user_ids", 999)])
    assert response.status_code == 200
    found_users = response.json()
    assert len(found_users) == 2
    assert {user["id"] for user in found_users} == {1, 2}

    response = client.post("/users/many", json=[])
    assert response.status_code == 200
    assert response.json() == []


def test_auth_register_and_duplicate(client: TestClient) -> None:
    response = register_user(client)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["username"] == "alice"
    assert created_user["email"] == "alice@example.com"
    assert created_user["id"] == 1

    response = register_user(client)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_auth_login_and_refresh_flow(client: TestClient) -> None:
    register_user(client)

    response = login_user(client)
    assert response.status_code == 200
    tokens = response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    refreshed_tokens = response.json()

    assert "access_token" in refreshed_tokens
    assert "refresh_token" in refreshed_tokens
    assert refreshed_tokens["token_type"] == "bearer"


def test_auth_login_invalid_credentials(client: TestClient) -> None:
    register_user(client)

    response = login_user(client, password="wrong123")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}

    response = login_user(client, email="missing@example.com", password="123456")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_refresh_rejects_access_token(client: TestClient) -> None:
    register_user(client)
    response = login_user(client)
    tokens = response.json()

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid refresh token"}


def test_dependency_auth_flow(client: TestClient) -> None:
    register_user(client)
    response = login_user(client)
    tokens = response.json()

    response = client.get("/auth/me-dep", headers=auth_headers(tokens["access_token"]))
    assert response.status_code == 200
    me = response.json()
    assert me["username"] == "alice"
    assert me["email"] == "alice@example.com"
    assert me["id"] == 1

    response = client.get("/auth/me-dep")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = client.get("/auth/me-dep", headers=auth_headers("broken.token.value"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

    response = client.get("/auth/me-dep", headers=auth_headers(tokens["refresh_token"]))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token type"}


def test_middleware_auth_flow(client: TestClient) -> None:
    register_user(client)
    response = login_user(client)
    tokens = response.json()

    response = client.get("/auth/me-middleware", headers=auth_headers(tokens["access_token"]))
    assert response.status_code == 200
    me = response.json()
    assert me["username"] == "alice"
    assert me["email"] == "alice@example.com"
    assert me["id"] == 1

    response = client.get("/auth/me-middleware")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = client.get("/auth/me-middleware", headers=auth_headers("broken.token.value"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

    response = client.get("/auth/me-middleware", headers=auth_headers(tokens["refresh_token"]))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token type"}


def test_get_nonexistent_user_returns_404(client: TestClient) -> None:
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_update_nonexistent_user_returns_404(client: TestClient) -> None:
    response = client.put(
        "/users/999",
        json={"email": "missing@example.com"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_delete_nonexistent_user_returns_404(client: TestClient) -> None:
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.parametrize(
    "payload",
    [
        {
            "username": "ab",  # слишком короткий username
            "email": "john@example.com",
            "password": "123456",
        },
        {
            "username": "john",
            "email": "not-an-email",  # невалидный email
            "password": "123456",
        },
        {
            "username": "john",
            "email": "john@example.com",
            "password": "123",  # слишком короткий password
        },
    ],
)
def test_create_user_validation_errors(client: TestClient, payload: dict) -> None:
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {
            "username": "ab",
            "email": "alice@example.com",
            "password": "123456",
        },
        {
            "username": "alice",
            "email": "wrong-email",
            "password": "123456",
        },
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "123",
        },
    ],
)
def test_auth_register_validation_errors(client: TestClient, payload: dict) -> None:
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_auth_login_validation_error_for_bad_email_shape(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "123456",
        },
    )
    assert response.status_code == 422


def test_refresh_validation_error_when_field_missing(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={})
    assert response.status_code == 422


def test_middleware_rejects_invalid_authorization_header(client: TestClient) -> None:
    register_user(client)
    login_response = login_user(client)
    assert login_response.status_code == 200

    response = client.get(
        "/auth/me-middleware",
        headers={"Authorization": "Basic abc123"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authorization header"}

    response = client.get(
        "/auth/me-middleware",
        headers={"Authorization": "Bearer"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authorization header"}


def create_project_owner(client: TestClient) -> int:
    response = client.post(
        "/users/",
        json={
            "username": "owner1",
            "email": "owner1@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def create_project(
    client: TestClient,
    owner_id: int,
    name: str = "Project One",
    status: str = "new",
):
    return client.post(
        "/projects/",
        json={
            "name": name,
            "description": f"{name} description",
            "status": status,
            "person_in_charge_id": owner_id,
        },
    )


def test_project_crud_flow(client: TestClient) -> None:
    owner_id = create_project_owner(client)

    response = create_project(client, owner_id)
    assert response.status_code == 200
    created_project = response.json()

    assert created_project["name"] == "Project One"
    assert created_project["status"] == "new"
    assert created_project["person_in_charge_id"] == owner_id
    assert "id" in created_project
    assert "create_time" in created_project

    project_id = created_project["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "name": "Updated Project",
            "status": "completed",
        },
    )
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["name"] == "Updated Project"
    assert updated_project["status"] == "completed"

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_project_list_pagination_filtering_and_sorting(client: TestClient) -> None:
    owner_id = create_project_owner(client)

    response = client.post(
        "/projects/many",
        json=[
            {
                "name": "Project A",
                "description": "A",
                "status": "new",
                "person_in_charge_id": owner_id,
            },
            {
                "name": "Project B",
                "description": "B",
                "status": "in_progress",
                "person_in_charge_id": owner_id,
            },
            {
                "name": "Project C",
                "description": "C",
                "status": "new",
                "person_in_charge_id": owner_id,
            },
        ],
    )
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get("/projects/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total_count"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["has_prev"] is False
    assert data["has_next"] is True

    response = client.get("/projects/", params={"status": "new"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
    assert {project["status"] for project in data["items"]} == {"new"}

    response = client.get(
        "/projects/",
        params={"person_in_charge_id": owner_id},
    )
    assert response.status_code == 200
    assert response.json()["total_count"] == 3

    response = client.get(
        "/projects/",
        params={"sort_by": "create_time"},
    )
    assert response.status_code == 200

    response = client.get(
        "/projects/",
        params={"sort_by": "wrong_field"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid sort_by field"}


def test_project_errors_and_validation(client: TestClient) -> None:
    owner_id = create_project_owner(client)

    response = create_project(client, owner_id, name="Unique Project")
    assert response.status_code == 200
    project_id = response.json()["id"]

    response = create_project(client, owner_id, name="Unique Project")
    assert response.status_code == 409
    assert response.json() == {"detail": "Project with this name already exists"}

    response = create_project(client, 999, name="Wrong Owner Project")
    assert response.status_code == 400
    assert response.json() == {"detail": "Person in charge not found"}

    response = client.patch("/projects/999", json={"name": "Missing Project"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

    response = client.delete("/projects/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

    response = client.patch(
        f"/projects/{project_id}",
        json={"create_time": "2026-01-01T00:00:00"},
    )
    assert response.status_code == 422
