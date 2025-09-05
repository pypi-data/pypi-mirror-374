from sqlite3 import Connection

from raphson_mp.common.music import Album
from raphson_mp.server.track import FileTrack, Track


def process_query(query: str) -> str:
    return '"' + query.replace('"', '""').replace(" ", '" OR "') + '"'


def search_tracks(conn: Connection, query: str, limit: int = 25, offset: int = 0) -> list[Track]:
    result = conn.execute(
        f"""
        SELECT track_fts.path
        FROM track_fts
        WHERE track_fts MATCH ?
        ORDER BY rank
        LIMIT {limit} OFFSET {offset}
        """,
        (process_query(query),),
    )
    return [FileTrack(conn, relpath) for relpath, in result]


def search_albums(conn: Connection, query: str, limit: int = 10, offset: int = 0) -> list[Album]:
    return [
        Album(name, artist, track)
        for track, name, artist in conn.execute(
            f"""
            SELECT path, album, album_artist
            FROM track
            WHERE path IN (
                SELECT path
                FROM track_fts
                WHERE track_fts.album MATCH :query OR track_fts.album_artist MATCH :query OR track_fts.artists MATCH :query
                ORDER BY rank
            )
                AND album IS NOT NULL
            GROUP BY album, album_artist
            LIMIT {limit} OFFSET {offset}
            """,
            {"query": process_query(query)},
        )
    ]
