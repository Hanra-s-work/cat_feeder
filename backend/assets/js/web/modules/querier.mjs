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
* FILE: querier.mjs
* CREATION DATE: 25-01-2026
* LAST Modified: 3:31:17 25-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the querier module in charge of providing an interface between the fetch library and the rest interface.
* // AR
* +==== END CatFeeder =================+
*/
/*
** EPITECH PROJECT, 2024
** area-rattrapage
** File description:
** querier.mjs
*/

console.log("js/querier initialising");

const script = document.querySelector(`script[src="${new URL(import.meta.url).pathname}"]`);
const url = script?.dataset.apiUrl ?? "http://127.0.0.1:5000";
const port = script?.dataset.apiPort ? Number(script.dataset.apiPort) : -1;

console.log("script = " + script);
console.log(`url = ${url}, port = ${port}`);

async function query(method = "GET", path = "/", body = null, token = "") {
    try {
        const headers = {};

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const payload = {
            method: method,
            mode: "cors",
            headers: headers,
        };

        if (method !== "GET" && body) {
            if (body instanceof FormData) {
                payload.body = body;
                // Content-Type will be set automatically for FormData
            } else {
                headers['Content-Type'] = 'application/json';
                payload.body = JSON.stringify(body);
            }
        }

        let final_url;

        if (port === -1) {
            final_url = `${url}${path}`;
        } else {
            final_url = `${url}:${port}${path}`;
        }
        console.log("Final URL:", final_url);
        console.log("Payload:", payload);
        const response = await fetch(final_url, payload);
        console.log(response);
        const text = await response.text();
        let data = {};
        try {
            data = JSON.parse(text);
        } catch (e) {
            data = { message: text };
        }
        data.status = response.status;
        data.ok = response.ok;
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return { ok: false, status: 0, message: error.message };
    }
}

async function get(path = "/", body = {}, token = "") {
    return await query("GET", path, body, token);
}

async function put(path = "/", body = {}, token = "") {
    return await query("PUT", path, body, token);
}

async function post(path = "/", body = {}, token = "") {
    return await query("POST", path, body, token);
}

async function patch(path = "/", body = {}, token = "") {
    return await query("PATCH", path, body, token);
}

async function delete_query(path = "/", body = {}, token = "") {
    return await query("DELETE", path, body, token);
}

const queries = {
    query,
    get,
    put,
    post,
    patch,
    delete_query
};

export { queries };

window.querier = queries;

console.log("js/querier initialised");
