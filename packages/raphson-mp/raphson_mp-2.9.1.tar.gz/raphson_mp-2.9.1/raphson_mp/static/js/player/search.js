import { eventBus, MusicEvent } from "./event.js";
import { music, Track, Album } from "../api.js";
import { AlbumBrowse, ArtistBrowse, browse, getTracksTable } from "./browse.js";
import { windows } from "./window.js";

class Search {
    #searchResultParent = /** @type {HTMLDivElement} */ (document.getElementById('search-result-parent'));
    #searchResultTracks = /** @type {HTMLTableSectionElement} */ (document.getElementById('search-result-tracks'));
    #searchResultArtists = /** @type {HTMLDivElement} */ (document.getElementById('search-result-artists'));
    #searchResultAlbums = /** @type {HTMLDivElement} */ (document.getElementById('search-result-albums'));
    #queryInput = /** @type {HTMLInputElement} */ (document.getElementById('search-query'));
    #openButton = /** @type {HTMLButtonElement} */ (document.getElementById('open-window-search'));
    /** @type {number | null} */
    #searchTimeoutId = null;

    constructor() {
        eventBus.subscribe(MusicEvent.METADATA_CHANGE, () => {
            if (!windows.isOpen('window-search')) {
                console.debug('search: ignore METADATA_CHANGE, search window is not open');
                return;
            }
            console.debug('search: search again after receiving METADATA_CHANGE event');
            this.#performSearch(true);
        });

        this.#queryInput.addEventListener('input', () => this.#performSearch());
        this.#openButton.addEventListener('click', () => this.openSearchWindow());
    }

    openSearchWindow() {
        const queryField =  /** @type {HTMLInputElement} */ (document.getElementById('search-query'));
        queryField.value = '';
        // @ts-ignore
        setTimeout(() => queryField.focus({ focusVisible: true }), 50); // high delay is necessary, I don't know why
        this.#searchResultParent.hidden = true;
    }

    async #performSearch(searchNow = false) {
        // Only start searching after user has finished typing for better performance and fewer network requests
        if (!searchNow) {
            // Reset timer when new change is received
            if (this.#searchTimeoutId != null) {
                clearTimeout(this.#searchTimeoutId);
            }
            // Perform actual search in 200 ms
            this.#searchTimeoutId = setTimeout(() => this.#performSearch(true), 200);
            return;
        }

        const query = this.#queryInput.value;

        /** @type {Array<Track>} */
        let tracks = [];
        /** @type {Array<Album>} */
        let albums = [];
        if (query.length > 1) {
            const result = await music.search(query);
            tracks = result.tracks;
            albums = result.albums;
        } else {
            tracks = [];
            albums = [];
        }

        if (tracks.length == 0) {
            this.#searchResultParent.hidden = true;
            return;
        }

        this.#searchResultParent.hidden = false;

        // Tracks
        {
            this.#searchResultTracks.replaceChildren(getTracksTable(tracks));
        }

        // Artists
        {
            const table = document.createElement('table');
            const listedArtists = new Set(); // to prevent duplicates, but is not actually used to preserve ordering
            for (const track of tracks) {
                if (track.artists.length == 0) {
                    continue;
                }

                for (const artist of track.artists) {
                    if (listedArtists.has(artist)) {
                        continue;
                    }
                    listedArtists.add(artist);

                    const artistLink = document.createElement('a');
                    artistLink.textContent = artist;
                    artistLink.onclick = () => browse.browse(new ArtistBrowse(artist));

                    const td = document.createElement('td');
                    td.append(artistLink);
                    const row = document.createElement('tr');
                    row.append(td);
                    table.append(row);
                }
            }

            this.#searchResultArtists.replaceChildren(table);
        }

        // Albums
        {
            const coverSize = '12rem';
            const newChildren = [];
            for (const album of albums) {
                const text = document.createElement('div');
                text.textContent = album.name;
                text.classList.add('box-header', 'line');

                const img = document.createElement('div');
                const imgUri = album.getCoverURL('low');
                img.style.background = `black url("${imgUri}") no-repeat center / cover`;
                img.style.height = coverSize;

                const result = document.createElement('div');
                result.classList.add('box');
                result.style.width = coverSize;
                result.addEventListener('click', () => browse.browse(new AlbumBrowse(album)));
                result.append(text, img);

                newChildren.push(result);

                if (newChildren.length > 6) {
                    break;
                }
            }

            this.#searchResultAlbums.replaceChildren(...newChildren);
        }
    }
}

export const search = new Search();
