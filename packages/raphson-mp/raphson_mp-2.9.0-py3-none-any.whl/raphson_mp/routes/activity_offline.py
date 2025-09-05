from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server import auth
from raphson_mp.server.decorators import route


@route("/played", method="POST")
async def route_played(request: web.Request, conn: Connection, _user: auth.User):
    json = await request.json()
    track = cast(str, json["track"])
    timestamp = cast(int, json["timestamp"])
    conn.execute("INSERT INTO history VALUES (?, ?)", (timestamp, track))
    raise web.HTTPNoContent()
