import { eventBus, MusicEvent } from "./event.js";
import { queue } from "./queue.js";
import { TimeSyncedLyrics, PlainLyrics, Lyrics, parseLyrics } from "../api.js";
import { coverSize } from "./coversize.js";
import { player } from "./player.js";
import { createToast, vars } from "../util.js";

class PlayerLyrics {
    #lyricsSetting = /** @type {HTMLInputElement} */ (document.getElementById("settings-lyrics"));
    #lyricsBox = /** @type {HTMLDivElement} */ (document.getElementById('lyrics-box'));
    #albumCoverBox = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-box'));
    #lyrics = /** @type {Lyrics | null} */ (null);
    /** @type {number | null} */
    #lastLine = null;
    #updateSyncedLyricsListener;

    constructor() {
        this.#updateSyncedLyricsListener = () => this.#updateSyncedLyrics();

        // Quick toggle for lyrics setting
        this.#albumCoverBox.addEventListener('click', () => this.toggleLyrics());

        // Listener is only registered if page is visible, so if page visibility
        // changes we must register (or unregister) the listener.
        document.addEventListener('visibilitychange', () => this.#updateLyrics());

        // Handle lyrics setting being changed
        this.#lyricsSetting.addEventListener('change', () => {
            this.#updateLyrics();
            coverSize.resizeCover();
        });

        eventBus.subscribe(MusicEvent.TRACK_CHANGE, async () => {
            const track = queue.currentTrack;
            if (track) {
                this.#lyrics = parseLyrics(track.lyrics);
            } else {
                this.#lyrics = null;
            }
            // When lyrics change, current state is no longer accurate
            this.#lastLine = null;
            this.#updateLyrics();
        });
    }

    toggleLyrics() {
        this.#lyricsSetting.checked = !this.#lyricsSetting.checked;
        this.#lyricsSetting.dispatchEvent(new Event('change'));
        if (this.#lyricsSetting.checked) {
            createToast('text-box', vars.tLyricsEnabled, vars.tLyricsDisabled);
        } else {
            createToast('text-box', vars.tLyricsDisabled, vars.tLyricsEnabled);
        }
    }

    #updateSyncedLyrics() {
        const position = player.getPosition();

        if (!this.#lyrics || !(this.#lyrics instanceof TimeSyncedLyrics) || position === null) {
            throw new Error();
        }

        const currentLine = this.#lyrics.currentLine(position);

        if (currentLine == this.#lastLine) {
            // Still the same line, no need to cause expensive DOM update.
            return;
        }

        this.#lastLine = currentLine;

        // Show current line, with context
        const context = 3;
        const lyricsHtml = [];
        for (let i = currentLine - context; i <= currentLine + context; i++) {
            if (i >= 0 && i < this.#lyrics.text.length) {
                const lineHtml = document.createElement('span');
                lineHtml.textContent = this.#lyrics.text[i].text;
                if (i != currentLine) {
                    lineHtml.classList.add('secondary-large');
                }
                lyricsHtml.push(lineHtml);
            }
            lyricsHtml.push(document.createElement('br'));
        }

        this.#lyricsBox.replaceChildren(...lyricsHtml);
    }

    #updateLyrics() {
        eventBus.unsubscribe(MusicEvent.PLAYER_POSITION, this.#updateSyncedLyricsListener);

        if (document.visibilityState != 'visible') {
            return;
        }

        if (this.#lyricsSetting.checked && this.#lyrics) {
            this.#lyricsBox.hidden = false;
            if (this.#lyrics instanceof TimeSyncedLyrics) {
                eventBus.subscribe(MusicEvent.PLAYER_POSITION, this.#updateSyncedLyricsListener);
                // also trigger immediate update, especially necessary when audio is paused and no timeupdate events will be triggered
                this.#updateSyncedLyrics();
            } else if (this.#lyrics instanceof PlainLyrics) {
                if (this.#lyrics.text == "[Instrumental]") {
                    const instrumentalHtml = document.createElement('p');
                    instrumentalHtml.classList.add('secondary-large');
                    instrumentalHtml.textContent = vars.tInstrumental;
                    this.#lyricsBox.replaceChildren(instrumentalHtml);
                } else {
                    this.#lyricsBox.textContent = this.#lyrics.text;
                }
            }
        } else {
            this.#lyricsBox.hidden = true;
        }
    }
}

export const lyrics = new PlayerLyrics();
