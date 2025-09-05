import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from sqlite3 import Connection
from threading import Thread
from typing import cast

from raphson_mp.client.playlist import Playlist
from raphson_mp.server import db, settings
from tests import set_dirs


async def test_migrate():
    temp_fresh = Path(tempfile.mkdtemp("test_migrate_fresh"))
    temp_migrate = Path(tempfile.mkdtemp("test_migrate_migrate"))
    try:
        settings.data_dir = temp_fresh
        # Test database initialization completes without errors (e.g. no SQL syntax errors)
        await db.migrate()

        # Make sure auto vacuum is enabled
        for database in db.DATABASES:
            with database.connect() as conn:
                auto_vacuum = cast(int, conn.execute("PRAGMA auto_vacuum").fetchone()[0])
                assert auto_vacuum == 2

        settings.data_dir = temp_migrate

        # Initialize database how it would be when the migration system was first introduced
        # Not a great test because the tables have no content, but it's better than nothing.
        # db_version_0 files obtained from:
        # https://codeberg.org/raphson/music-server/src/commit/2c501187/src/sql
        for database in db.DATABASES:
            init_sql = (Path(__file__).parent / "db_version_0" / f"{database.name}.sql").read_text(encoding="utf-8")
            await database.create(init_sql=init_sql)

        # Run through all migrations
        await db.migrate()

        # Check that database is up to date
        with db.META.connect() as conn:
            version = cast(int, conn.execute("SELECT version FROM db_version").fetchone()[0])
            assert version == len(db.get_migrations())

        # Make sure the migrated tables are equal to fresh tables
        for db_name in db._BY_NAME:
            command = ["sqldiff", "--schema", Path(temp_fresh, f"{db_name}.db"), Path(temp_migrate, f"{db_name}.db")]
            output = subprocess.check_output(command)
            assert output == b"", output.decode()
    finally:
        set_dirs()  # restore original data directory settings
        shutil.rmtree(temp_fresh)
        shutil.rmtree(temp_migrate)


def test_version():
    assert db.get_version().startswith("3.")


def test_write_read():
    """
    This tests whether a read-only database connection sees changes made by a
    different connection, without needing to re-open the read-only database connection.
    """
    test_db_dir = Path(tempfile.mkdtemp())
    try:
        test_db = Path(test_db_dir, "test.db")

        with db._new_connection(test_db) as conn:
            conn.execute("CREATE TABLE test (test TEXT)")

        def reader():
            with db._new_connection(test_db) as conn:
                for _i in range(20):
                    row = cast(tuple[str] | None, conn.execute("SELECT * FROM test").fetchone())
                    if row:
                        assert row[0] == "hello"
                        return
                    time.sleep(0.1)

            raise ValueError("did not read value")

        thread = Thread(target=reader)
        thread.start()
        time.sleep(0.5)
        with db._new_connection(test_db, False) as conn:
            conn.execute('INSERT INTO test VALUES ("hello")')
        thread.join()
    finally:
        shutil.rmtree(test_db_dir)


def test_fts_triggers(conn: Connection, playlist: Playlist):
    path = f"{playlist.name}/{secrets.token_urlsafe()}"

    try:
        # add track
        conn.execute(
            """
            INSERT INTO track (path, playlist, duration, title, album, album_artist, mtime, ctime)
            VALUES (?, ?, 20, 'TestTitle', 'TestAlbum', 'TestAlbumArtist', 0, 0)
            """,
            (path, playlist.name),
        )

        # add artists
        conn.execute("INSERT INTO track_artist VALUES (:path, 'TestArtist1'), (:path, 'TestArtist2')", {"path": path})

        # track should now also exist in FTS table
        title, album, album_artist, artists = conn.execute(
            "SELECT title, album, album_artist, artists FROM track_fts WHERE path = ?", (path,)
        ).fetchone()
        assert title == "TestTitle"
        assert album == "TestAlbum"
        assert album_artist == "TestAlbumArtist"
        assert artists == "TestArtist1 TestArtist2"

        # add one more artist
        conn.execute("INSERT INTO track_artist VALUES (?, 'TestArtist3')", (path,))
        (artists,) = conn.execute("SELECT artists FROM track_fts WHERE path = ?", (path,)).fetchone()
        assert artists == "TestArtist1 TestArtist2 TestArtist3"

        # modify track
        conn.execute(
            "UPDATE track SET title = 'TestTitle2', album = 'TestAlbum2', album_artist = 'TestAlbumArtist2' WHERE path = ?",
            (path,),
        )
        title, album, album_artist, artists = conn.execute(
            "SELECT title, album, album_artist, artists FROM track_fts WHERE path = ?", (path,)
        ).fetchone()
        assert title == "TestTitle2"
        assert album == "TestAlbum2"
        assert album_artist == "TestAlbumArtist2"
        assert artists == "TestArtist1 TestArtist2 TestArtist3"

        # delete track
        conn.execute("DELETE FROM track WHERE path = ?", (path,))
        assert conn.execute("SELECT * FROM track_fts WHERE path = ?", (path,)).fetchone() is None
    finally:
        # clean up
        conn.execute("DELETE FROM track WHERE path = ?", (path,))
