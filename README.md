# 北航电表查询 Telegram Bot

欢迎大家贡献/重构～

## 依赖项

* python 3.7
* python-telegram-bot == 12.0.0b1
* pydblite
* pyquery
* requests

## 使用说明

主程序是 tg.py 。运行时请给予工作目录的相应权限。

请在工作目录下建立 config.json 文件，并按以下格式编辑

```json
{
    "BotToken":"<此处填写你的 botToken>",
    "BaseURL":"https://api.telegram.org/bot",
    "DBFile":"data.sqlite3"
}
```

