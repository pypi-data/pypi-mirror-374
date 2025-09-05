from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.playlist import Playlist
from raphson_mp.common import util

from . import T_client, assert_html


async def test_stats_page(http_client: T_client):
    await assert_html(http_client, "/playlist/stats")


async def test_share_page(http_client: T_client, playlist: Playlist):
    await assert_html(http_client, "/playlist/share?playlist=" + util.urlencode(playlist.name))


async def test_list(client: RaphsonMusicClient):
    await client.playlists()


async def test_choose_track(client: RaphsonMusicClient, nonempty_playlist: Playlist):
    await client.choose_track(nonempty_playlist)
