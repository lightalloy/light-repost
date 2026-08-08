from app.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "tok")
    monkeypatch.setenv("CHANNEL_ID", "-100111")
    monkeypatch.setenv("VK_TOKEN", "vk-tok")
    monkeypatch.setenv("VK_GROUP_ID", "999")

    settings = Settings(_env_file=None)

    assert settings.bot_token == "tok"
    assert settings.channel_id == -100111
    assert settings.vk_token == "vk-tok"
    assert settings.vk_group_id == 999
