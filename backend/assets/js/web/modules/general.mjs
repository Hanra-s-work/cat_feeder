/* 
* +==== BEGIN CatFeeder =================+
* LOGO: 
* ..............(..../\
* ...............)..(.')
* ..............(../..)
* ...............\(__)|
* Inspired by Joan Stark
* source https://www.asciiart.eu/
* animals/cats
* /STOP
* PROJECT: CatFeeder
* FILE: general.mjs
* CREATION DATE: 25-01-2026
* LAST Modified: 2:21:29 25-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the javascript module that aims to contain the code that is specific to the website but most likely used in all the website.
* // AR
* +==== END CatFeeder =================+
*/

/*
 * Initialize the theme toggler for pages. This function is intentionally
 * self-contained and must be called explicitly (no top-level execution).
*/

function getCurrentTheme() {
    const select = document.getElementById("theme-select");

    let saved = "";
    if (typeof cookie !== "undefined" && cookie && cookie.readCookie) {
        saved = cookie.readCookie("theme");
    } else if (window.cookie_manager && window.cookie_manager.readCookie) {
        saved = window.cookie_manager.readCookie("theme");
    } else {
        saved = "";
    }

    if (saved) {
        applyTheme(saved);
        if (select) select.value = saved;
    } else if (select) {
        select.value = "system";
    }

    if (!select) {
        return;
    }
    return select;
}
function applyTheme(t) {
    if (t === "system" || !t) {
        document.documentElement.removeAttribute("data-theme");
    } else {
        document.documentElement.setAttribute("data-theme", t);
    }
}
function handleThemeChange(e) {
    const v = e.target.value;
    applyTheme(v);
    const expires = new Date(Date.now() + 31536000000).toUTCString(); // 1 year
    try {
        if (typeof cookie !== "undefined" && cookie && cookie.createCookie) {
            cookie.createCookie("theme", v, expires, "/");
        } else if (window.cookie_manager && window.cookie_manager.createCookie) {
            window.cookie_manager.createCookie("theme", v, expires, "/");
        } else {
            document.cookie = "theme=" + v + "; expires=" + expires + "; path=/; samesite=Lax";
        }
    } catch (err) {
        console.error("Failed to save theme cookie:", err);
    }
}
function initThemeToggler() {
    const select = getCurrentTheme();
    if (!select) return;
    select.addEventListener("change", handleThemeChange);
}

const generalScripts = {
    initThemeToggler,
    applyTheme,
    handleThemeChange,
    getCurrentTheme
}
export { generalScripts };
window.general_scripts = generalScripts;

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggler();
});
