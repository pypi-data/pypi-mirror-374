# Offline mode

The music player has an 'offline mode'. In this mode, the application:

- Does not make any connections to the internet.
- Does not transcode audio or images, always uses high quality opus audio and webp images.
- Does not use a local music library, but synchronizes from a main music server.
- Keeps a local history, which it submits to the main music server when a sync is started.

Example of the offline music player running on a tablet in [a car](https://projects.raphson.nl/projects/tyrone/):
![Music player in dashboard](tyrone_music.jpg)

## Installation

To install the music player in offline mode, run:
```
pipx install 'raphson-mp[offline]'
```

If you want to use the music player in both online and offline mode, you can install both sets of dependencies:
```
pipx install 'raphson-mp[online,offline]'
```

To start the music player in offline mode, run `raphson-mp` as usual, but now with the `--offline` flag. Example: `raphson-mp --offline start`

The container version can also be used in offline mode. Set the environment variable: `MUSIC_OFFLINE_MODE: 1`.

## Synchronization

To synchronize history and music, visit: http://localhost:8080/offline/sync

If you prefer the command line, or if you want to automate syncing, use: `raphson-mp sync`

## Start on boot

On a Linux system, you can create a systemd user service to start the music server on boot.

Create a service file, e.g. `.config/systemd/user/music.service` with the following contents:

```
[Unit]
Description=Music Player

[Service]
ExecStart=/home/youruser/.local/bin/raphson-mp --offline --data-dir /home/youruser/music-data start
Restart=always

[Install]
WantedBy=default.target
```

You might need to change the path to the `raphson-mp` executable or the data directory.

Reload: `systemctl --user daemon-reload`

Enable and start the service: `systemctl --user enable --now music`
