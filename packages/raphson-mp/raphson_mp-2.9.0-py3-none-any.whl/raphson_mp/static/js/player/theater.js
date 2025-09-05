import { vars, createToast } from "../util.js";
import { eventBus, MusicEvent } from "./event.js";

const THEATER_TIMEOUT = 5_000;

class Theater {
    #htmlSetting = /** @type {HTMLInputElement} */ (document.getElementById("settings-theater"));
    #htmlBody = document.getElementsByTagName('body')[0];
    /** @type {(() => void) | null} */
    #listenerFunction;
    /** @type {number} */
    #enableTimer = 0;

    constructor() {
        this.#htmlSetting.addEventListener('change', () => this.#onSettingChange());
        eventBus.subscribe(MusicEvent.SETTINGS_LOADED, () => this.#onSettingChange());
    }

    toggle() {
        console.debug('theater: toggled setting');
        this.#htmlSetting.checked = !this.#htmlSetting.checked;
        this.#onSettingChange();
        if (this.#htmlSetting.checked) {
            createToast('fullscreen', vars.tTheaterModeEnabled, vars.tTheaterModeDisabled);
        } else {
            createToast('fullscreen-exit', vars.tTheaterModeDisabled, vars.tTheaterModeEnabled);
        }
    }

    #onMove() {
        clearTimeout(this.#enableTimer);
        this.#startTimer();
        requestAnimationFrame(() => {
            this.#deactivate();
        });
    }

    #onSettingChange() {
        if (this.#listenerFunction) {
            console.debug('theater: unregistered listener');
            document.removeEventListener('pointermove', this.#listenerFunction);
            this.#listenerFunction = null;
        }

        const theaterModeEnabled = this.#htmlSetting.checked;
        if (theaterModeEnabled) {
            console.debug('theater: registered timer and listener');
            document.addEventListener('pointermove', this.#listenerFunction = () => this.#onMove());
            this.#startTimer();
            return;
        } else {
            clearInterval(this.#enableTimer);
            this.#deactivate();
        }
    }

    #startTimer() {
        // Activate theater mode, unless aborted by a mouse move
        this.#enableTimer = setTimeout(() => this.#activate(), THEATER_TIMEOUT);
    }

    #activate() {
        this.#htmlBody.classList.add('theater');
    }

    #deactivate() {
        this.#htmlBody.classList.remove('theater');
    }
}

export const theater = new Theater();
