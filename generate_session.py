from pyrogram import Client

api_id = 21321325
api_hash = "93e7c730ce8992e378b2225471f2f860"

with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
    print("SESSION_STRING:", app.export_session_string())
