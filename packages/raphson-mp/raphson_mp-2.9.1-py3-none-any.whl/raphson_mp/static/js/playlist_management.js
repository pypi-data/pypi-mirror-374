import { createToast, vars } from "./util.js";

const spotifySubmit = /** @type {HTMLInputElement} */ (document.getElementById('spotify-submit'));
const spotifyPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('spotify-playlist'));
const spotifyUrl = /** @type {HTMLInputElement} */ (document.getElementById('spotify-url'));

if (spotifySubmit) {
    spotifySubmit.addEventListener('click', () => {
        const playlist = spotifyPlaylist.value;

        let url = spotifyUrl.value;

        if (!url.startsWith('https://open.spotify.com/playlist/')) {
            createToast('icon-close', vars.tInvalidSpotifyPlaylistUrl);
            return;
        }

        url = url.substring('https://open.spotify.com/playlist/'.length);

        if (url.includes('?si')) {
            url = url.substring(0, url.indexOf('?si'));
        }

        window.location.assign(`/playlist_management/compare_spotify?playlist=${encodeURIComponent(playlist)}&spotify_playlist=${encodeURIComponent(url)}`);
    });
} else {
    console.warn("spotify is not available");
}
