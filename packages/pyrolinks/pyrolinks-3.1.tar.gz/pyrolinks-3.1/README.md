# PyroLinks
A simple Pyrogram-based module to create streaming download links for Telegram files !

```bash
pip install pyrolinks
```

**🍺Example**
```python
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrolinks.client import PyroLinks, compose
from pyrolinks.errors import PyroLinksError

app = Client(
    "pyrolinks",
    api_id=123456,
    api_hash="abcd",
    token="123:abc",
)

links = PyroLinks(
    app,
    schema="http",
    domain="example.com",
    ip="0.0.0.0",
    port=8080,
    route="/dl",
    logger=logging.getLogger("PyroLinks"),
)
@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handler(client, message: Message):
    try:
        link = await links.generate_link(message)
        await message.reply(f"✅ Direct link:\n{link}")
    except PyroLinksError as e:
        await message.reply(f"❌ Error: {e}")
compose([links])
```
