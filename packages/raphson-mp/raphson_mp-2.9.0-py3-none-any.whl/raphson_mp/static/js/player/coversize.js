// Ensures combined height of album cover and lyrics box never exceed 100vh

class CoverSize {
    #lyricsBox = /** @type {HTMLDivElement} */ (document.getElementById('lyrics-box'));
    #coverBox = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-box'));

    constructor() {
        const resizeObserver = new ResizeObserver(() => {
            // delay to avoid infinite resize loop
            setTimeout(() => this.resizeCover(), 0);
        });
        resizeObserver.observe(this.#lyricsBox);
        resizeObserver.observe(document.body);
    }

    /**
     * @param {string} value
     */
    #setMaxHeight(value) {
        this.#coverBox.style.maxHeight = value;
        this.#coverBox.style.maxWidth = value;
        this.#lyricsBox.style.maxWidth = value;
        console.debug('coversize: max height changed:', value);
    }

    resizeCover() {
        // Do not set max height in single column interface
        if (document.body.clientWidth <= 950) {
            this.#setMaxHeight('none');
            return;
        }

        if (this.#lyricsBox.hidden) {
            // No lyrics
            this.#setMaxHeight(`calc(100vh - 2*var(--gap))`);
            return;
        }

        this.#setMaxHeight(`calc(100vh - 3*var(--gap) - ${this.#lyricsBox.clientHeight}px)`);
    }
}

export const coverSize = new CoverSize();
