# Installation

## Pipx

Pipx can install Python programs, automatically installing dependencies in a virtual environment.

First install pipx using your system package manager. For example
* Debian: `sudo apt install pipx`
* Fedora: `sudo dnf install pipx`

You need at least Python 3.11.

After installing pipx, run:

```
pipx install 'raphson-mp[online]'
```

The music player is now available as the command `raphson-mp`.

Unless you are using the music player in [offline mode](./offline.md), you should also install:
* Debian: `sudo apt install ffmpeg libchromaprint-tools`
* Fedora: `sudo dnf install ffmpeg chromaprint-tools`

Start the server: `raphson-mp start`.

The music player uses two configurable directories to store data, [--data-dir](./databases.md) and [--music-dir](./music-files.md) which are documented by the linked pages.

## Container

Take the `compose.prod.yaml` compose file as a starting point.

Management tasks can be performed by running a second instance of the container:
```
docker compose run music --help
```

# Usage

Run `raphson-mp --help` for help.

Start the web server: `raphson-mp start`

Create an admin user: `raphson-mp useradd --admin yourusername`

Scan for file changes, if you've modified files directly: `raphson-mp scan`

By default, data is stored in ./data and ./music in your current working directory. To change this, use `--data-dir` and `--music-dir`. For more information, see [data-files](./data-files.md) and [music-files](./music-files.md).
