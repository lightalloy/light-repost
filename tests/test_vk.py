import httpx
import pytest
import respx

from app.services.vk import VK_API, wall_post


@pytest.mark.asyncio
@respx.mock
async def test_wall_post_returns_post_id():
    respx.post(f"{VK_API}/wall.post").mock(
        return_value=httpx.Response(200, json={"response": {"post_id": 42}})
    )

    post_id = await wall_post("hello")

    assert post_id == 42
    request = respx.calls.last.request
    assert b"message=hello" in request.content
    assert b"from_group=1" in request.content


@pytest.mark.asyncio
@respx.mock
async def test_wall_post_raises_on_vk_error():
    respx.post(f"{VK_API}/wall.post").mock(
        return_value=httpx.Response(
            200,
            json={"error": {"error_code": 27, "error_msg": "nope"}},
        )
    )

    with pytest.raises(RuntimeError, match="VK error"):
        await wall_post("hello")
