from aiohttp.web import HTTPBadRequest

from raphson_mp.client.playlist import Playlist
from raphson_mp.client.track import Track
from raphson_mp.common import util
from tests import T_client, assert_html


async def test_files(http_client: T_client):
    await assert_html(http_client, "/files")


async def test_rename(http_client: T_client, track: Track):
    await assert_html(http_client, "/files/rename?path=" + util.urlencode(track.path))


async def test_mkdir_exists(http_client: T_client, csrf_token: str, playlist: Playlist):
    async with http_client.post(
        "/files/mkdir", data={"path": "", "dirname": playlist.name, "csrf": csrf_token}
    ) as response:
        assert response.status == HTTPBadRequest.status_code
        assert "already exists" in await response.text()


async def test_download_file(http_client: T_client, track: Track):
    async with http_client.get("/files/download", params={"path": track.path}) as response:
        response.raise_for_status()


async def test_download_playlist(http_client: T_client, playlist: Playlist):
    async with http_client.get("/files/download", params={"path": playlist.name}) as response:
        response.raise_for_status()
        while _data := await response.content.read(1024 * 1024):
            pass
