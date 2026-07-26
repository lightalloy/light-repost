Автопостинг: пост в TG-канале → пост в одно VK-сообщество
Только текст (фото отложено: community token не умеет wall/album photo upload)
Всё в .env (токены, CHANNEL_ID, VK_GROUP_ID)
Docker + VPS — после того как локально заработает

-----------
Порядок реализации (маленькие шаги)

- Бот отвечает /start в личке (проверка, что токен живой) ✅
- Логировать channel_post (только текст) в консоль ✅
- wall.post текста в VK из хендлера ✅
- Docker
- webhook
- ссылки
- mapping/delete
- фото — позже, если найдём нормальный путь

--------------------
Docker:

```bash
docker compose up -d --build
docker compose logs -f bot
```

При webhook этой строки не будет: вместо неё поднимешь HTTP-сервер, а Telegram будет POST-ить апдейты на URL. Хендлеры (cmd_start) те же — меняется только способ доставки апдейтов
