import asyncio
import os
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import auth, logconfig
from raphson_mp.server.decorators import route
from raphson_mp.server.i18n import gettext
from raphson_mp.server.response import template


@route("", require_admin=True)
async def view(_request: web.Request, _conn: Connection, _user: auth.User):
    path = logconfig.error_logfile_path()
    size = path.stat().st_size
    if size == 0:
        error = gettext("Log file is empty")
        log_content = None
    elif size > 1024 * 1024:
        error = gettext("Log file is too large to be displayed")
        log_content = None
    else:
        error = None
        log_content = await asyncio.to_thread(path.read_text)

    return await template("log.jinja2", log_content=log_content, error=error)


@route("/clear", require_admin=True)
async def clear(_request: web.Request, _conn: Connection, _user: auth.User):
    os.truncate(logconfig.error_logfile_path(), 0)
    return web.HTTPSeeOther("/log")
