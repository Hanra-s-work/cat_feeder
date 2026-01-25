/*
** EPITECH PROJECT, 2024
** area-rattrapage
** File description:
** cookies.mjs
*/

console.log("js/cookie_dealing initialising");
function createMany(string) {
    document.cookie = string
}

function create(key = "0", value = "0", expires = "", path = "/") { //modifying cookie == create cookie
    document.cookie = key + "=" + value + "; expires=" + expires + "; path=" + path;
}

function read(key) { //from https://www.w3schools.com/js/js_cookies.asp
    var name = key + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function remove(key) {
    document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function createManyCookie(string) {
    document.cookie = string
}

function createCookie(key = "0", value = "0", expires = "", path = "/") { //modifying cookie == create cookie
    let content = key + "=" + value + "; expires=" + expires + "; path=" + path + ";samesite=Lax";
    document.cookie = content;
}

function readCookie(key) { //from https://www.w3schools.com/js/js_cookies.asp
    var name = key + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function removeCookie(key) {
    document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function clear_all_cookies() {
    var cookies = document.cookie;
    var cookies_array = cookies.split(";");
    for (var i = 0; i < cookies_array.length; i++) {
        var cookie = cookies_array[i];
        var cookie_name = cookie.split("=")[0];
        removeCookie(cookie_name);
    }
    console.log("Cookies cleared");
    alert("Cookies Cleared");
}

function count_all_cookies() {
    var cookies = document.cookie;
    var cookies_array = cookies.split(";");
    var cookie_count = 0;
    for (var i = 0; i < cookies_array.length; i++) {
        var cookie = cookies_array[i];
        var cookie_name = cookie.split("=")[0];
        if (cookie_name != "") {
            cookie_count++;
        }
    }
    return cookie_count;
}

function displayCookies() {
    const cookies = document.cookie.split("; ");
    if (cookies.length === 1 && cookies[0] === "") {
        console.log("No accessible cookies found.");
        return;
    }

    console.log("Accessible Cookies:");
    cookies.forEach(cookie => {
        const [name, value] = cookie.split("=");
        console.log(`Name: ${name}, Value: ${decodeURIComponent(value)}`);
    });
}

function display() {
    const cookies = document.cookie.split("; ");
    if (cookies.length === 1 && cookies[0] === "") {
        console.log("No accessible cookies found.");
        return;
    }

    console.log("Accessible Cookies:");
    cookies.forEach(cookie => {
        const [name, value] = cookie.split("=");
        console.log(`Name: ${name}, Value: ${decodeURIComponent(value)}`);
    });
}

console.log("js/cookie_dealing initialised");

const cookie = {
    createMany,
    create,
    read,
    remove,
    display,
    createManyCookie,
    createCookie,
    readCookie,
    removeCookie,
    displayCookies,
    clear_all_cookies,
    count_all_cookies
};

export { cookie }

window.cookie_manager = cookie;
