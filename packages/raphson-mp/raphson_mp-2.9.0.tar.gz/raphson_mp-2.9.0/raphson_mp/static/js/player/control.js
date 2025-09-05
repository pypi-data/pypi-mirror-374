import { controlChannel, ControlCommand, ControlTopic, Track } from "../api.js";
import { player, playerControls, playlistCheckboxes } from "./player.js";
import { queue, QueuedTrack } from "./queue.js";
import { eventBus, MusicEvent } from "./event.js";
import { createToast } from "../util.js";
import { vars } from "../util.js";

export let playerSync = /** @type {string | null} */ (null);
const SYNC_BANNER = /** @type {HTMLDivElement} */ (document.getElementById('sync-banner'));
const SYNC_BANNER_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('sync-banner-text'));

/**
 * @param {Array<import("../types.js").QueuedTrackJson>} tracks
 * @returns
 */
async function queueFromControlJson(tracks) {
    return await Promise.all(tracks.map(async track => {
        return new QueuedTrack(new Track(track.track), track.manual);
    }));
}

function queueToControlJson() {
    return queue.queuedTracks.map(queuedTrack => {
        return { manual: queuedTrack.manual, track: queuedTrack.track };
    });
}

// Send playing status to server
{
    const nameSetting = /** @type {HTMLButtonElement} */ (document.getElementById('settings-name'));

    async function updateNowPlaying() {
        if (queue.currentTrack == null) {
            return;
        }

        const data = {
            paused: player.isPaused(),
            position: player.getPosition(),
            duration: player.getDuration(),
            control: true,
            volume: playerControls.getVolume(),
            client: nameSetting.value,
            queue: queueToControlJson(),
            playlists: playlistCheckboxes.getActivePlaylists(),
            track: queue.currentTrack.toJson(),
        };

        if (data.duration == null) { // use duration from metadata if audio hasn't loaded yet and duration is unknown
            data.duration = queue.currentTrack.duration;
        }

        controlChannel.sendMessage(ControlCommand.CLIENT_PLAYING, data);
    }

    let timer = null;
    function throttledUpdate() {
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(updateNowPlaying, 10);
    }

    setInterval(throttledUpdate, 30_000);
    controlChannel.registerConnectHandler(throttledUpdate);
    nameSetting.addEventListener('input', throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_PLAY, throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_PAUSE, throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYER_SEEK, throttledUpdate);
    eventBus.subscribe(MusicEvent.QUEUE_CHANGE, throttledUpdate);
    eventBus.subscribe(MusicEvent.PLAYLIST_CHANGE, throttledUpdate);
    controlChannel.registerMessageHandler(ControlCommand.SERVER_REQUEST_UPDATE, throttledUpdate);
}

// Act on commands from server
{
    controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAY, () => {
        createToast('play', vars.tControlPlay);
        player.play();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PAUSE, () => {
        createToast('pause', vars.tControlPause);
        player.pause();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_PREVIOUS, () => {
        createToast('skip-previous', vars.tControlPrevious);
        queue.previous();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_NEXT, () => {
        createToast('skip-next', vars.tControlNext);
        queue.next();
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SEEK, (/** @type {import("../types.js").ControlClientSeek} */ data) => {
        createToast('play', vars.tControlSeek);
        player.seek(data.position, true);
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SET_QUEUE, async (/** @type {import("../types.js").ControlServerSetQueue} */ data) => {
        createToast('playlist-music', vars.tControlQueue);
        queue.queuedTracks = await queueFromControlJson(data.tracks);
        eventBus.publish(MusicEvent.QUEUE_CHANGE, true);
    });

    controlChannel.registerMessageHandler(ControlCommand.SERVER_SET_PLAYLISTS, async (/** @type {import("../types.js").ControlServerSetPlaylists} */ data) => {
        createToast('playlist-music', vars.tControlPlaylist);
        playlistCheckboxes.setActivePlaylists(data.playlists);
    });
}

// Sync with other player, if enabled
{
    let firstSync = true;

    // Sync currently playing
    controlChannel.registerMessageHandler(ControlCommand.SERVER_PLAYING, async (/** @type {import("../types.js").ControlServerPlaying} */ data) => {
        if (playerSync != data.player_id) return;

        if (data.queue == null || data.playlists == null) throw new Error("null queue or playlists");
        const remoteQueue = data.queue;
        const remotePlaylists = data.playlists;

        navigator.locks.request("control_sync", async () => {
            SYNC_BANNER.hidden = false;
            SYNC_BANNER_TEXT.textContent = data.username + (data.client ? " - " + data.client : "");

            // Current track
            if (queue.currentTrack == null || data.track.path != queue.currentTrack.path) {
                queue.currentTrack = new Track(data.track);
                eventBus.publish(MusicEvent.TRACK_CHANGE);

                // Wait for player to start playing, before the code below can update position
                if (!data.paused) {
                    try {
                        await player.play(true);
                    } catch (err) {
                        console.warn('control: cannot play, autoplay blocked?', err);
                    }
                }
            }

            // Position
            const position = player.getPosition();
            if (position != null && data.position != null && Math.abs(position - data.position) > 1) {
                console.debug('control: sync: seek');
                player.seek(data.position, true); // local=true to avoid seek loop
            }

            // Play/pause, must be after changing current track because TRACK_CHANGE event causes the track to start playing
            // Use local=true, player.pause() and player.play() do not need to send pause/play back to the remote server
            if (data.paused && !player.isPaused()) {
                console.debug('control: sync: pause');
                player.pause(true);
            } else if (!data.paused && player.isPaused()) {
                console.debug('control: sync: play');
                player.play(true);
            }

            // Playlists
            playlistCheckboxes.setActivePlaylists(remotePlaylists, true); // discreet=true to avoid loop

            // Queue
            queue.queuedTracks = await queueFromControlJson(remoteQueue);
            eventBus.publish(MusicEvent.QUEUE_CHANGE, true); // local=true to avoid loop

            if (firstSync) {
                firstSync = false;

                // Now that we are fully synced, we can register listeners to send modifications back to the remote player
                // We cannot do it before, or we risk sending wrong information to the remote player
                afterFirstSync();
            }
        });
    });

    function afterFirstSync() {
        // Send queue changes
        eventBus.subscribe(MusicEvent.QUEUE_CHANGE, (/** @type {boolean} */ local) => {
            // If player sync is active, set queue for remote player
            if (!local && playerSync != null) {
                console.debug('control: sync: playlists');
                controlChannel.sendMessage(ControlCommand.CLIENT_SET_QUEUE, { player_id: playerSync, tracks: queueToControlJson() });
            }
        });

        // Send playlist changes
        eventBus.subscribe(MusicEvent.PLAYLIST_CHANGE, () => {
            if (playerSync != null) { // local check not needed here, because in the code above, playlists are changed without triggering PLAYLIST_CHANGE
                controlChannel.sendMessage(ControlCommand.CLIENT_SET_PLAYLISTS, { player_id: playerSync, playlists: playlistCheckboxes.getActivePlaylists() });
            }
        });
    }
}

// Try to initialize player sync from URL
controlChannel.registerConnectHandler(() => {
    if (window.location.hash != "") {
        const playerId = window.location.hash.substring(1);

        console.debug('control: sync: start:', playerId);
        playerSync = playerId;
        playlistCheckboxes.disableSaving();
        controlChannel.subscribe(ControlTopic.ACTIVITY);

        // Request the server to send playing activity for this player
        controlChannel.sendMessage(ControlCommand.CLIENT_REQUEST_UPDATE, { player_id: playerId });
    }
});
