import os

# До импорта app.* — Settings() читает env при загрузке модуля.
os.environ.setdefault("BOT_TOKEN", "test-bot-token")
os.environ.setdefault("CHANNEL_ID", "-1001234567890")
os.environ.setdefault("VK_TOKEN", "test-vk-token")
os.environ.setdefault("VK_GROUP_ID", "123456")
