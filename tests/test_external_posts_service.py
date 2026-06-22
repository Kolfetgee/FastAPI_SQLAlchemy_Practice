import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.apps.external.services import ExternalPostsService


@pytest.mark.services
async def test_external_posts_service_get_posts():
    fake_posts = [
        {
            "userId": 1,
            "id": 1,
            "title": "Test title",
            "body": "Test body",
        }
    ]

    mock_response = Mock()
    mock_response.json.return_value = fake_posts
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client
    mock_context_manager.__aexit__.return_value = None

    with patch(
        "src.apps.external.services.httpx.AsyncClient",
        return_value=mock_context_manager,
    ):
        service = ExternalPostsService()

        result = await service.get_posts()

    assert result == fake_posts
    mock_client.get.assert_awaited_once_with(
        "https://jsonplaceholder.typicode.com/posts"
    )
    mock_response.raise_for_status.assert_called_once()