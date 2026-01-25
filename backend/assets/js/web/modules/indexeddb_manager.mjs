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
* FILE: indexeddb_manager.mjs
* CREATION DATE: 25-01-2026
* LAST Modified: 3:31:12 25-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the module to help handle indexeddb values in the browser.
* // AR
* +==== END CatFeeder =================+
*/
/*
** EPITECH PROJECT, 2024
** area-rattrapage
** File description:
** db_manager.mjs
*/

console.log("js/indexeddb_manager initialising");

const script = document.querySelector(`script[src="${new URL(import.meta.url).pathname}"]`);
const DB_NAME = script?.dataset.dbName ?? "catFeeder";
const STORE_NAME = script?.dataset.storeName ?? "keyValueStore";

console.log("script = " + script);
console.log(`DB_NAME = ${DB_NAME}, STORE_NAME = ${STORE_NAME}`);

function openDB(callback) {
    let request = indexedDB.open(DB_NAME, 1);

    request.onupgradeneeded = function (event) {
        let db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
            db.createObjectStore(STORE_NAME, { keyPath: "key" });
        }
    };

    request.onsuccess = function (event) {
        callback(event.target.result);
    };

    request.onerror = function (event) {
        console.error("IndexedDB error:", event.target.errorCode);
    };
}

function create(key, value) {
    openDB(db => {
        let transaction = db.transaction(STORE_NAME, "readwrite");
        let store = transaction.objectStore(STORE_NAME);
        store.put({ key, value });
    });
}

async function read(key) {
    const value = await new Promise((resolve, reject) => {
        openDB(db => {
            let transaction = db.transaction(STORE_NAME, "readonly");
            let store = transaction.objectStore(STORE_NAME);
            let request = store.get(key);

            request.onsuccess = function () {
                resolve(request.result ? request.result.value : null);
            };

            request.onerror = function () {
                reject(request.error || new Error("Failed to fetch value"));
            };
        });
    });

    console.log(`Value for key ${key}: ${value}`);
    return value;
}

function remove(key) {
    openDB(db => {
        let transaction = db.transaction(STORE_NAME, "readwrite");
        let store = transaction.objectStore(STORE_NAME);
        store.delete(key);
    });
}

function display() {
    openDB(db => {
        let transaction = db.transaction(STORE_NAME, "readonly");
        let store = transaction.objectStore(STORE_NAME);
        let request = store.openCursor();
        console.log("Stored Entries:");

        request.onsuccess = function (event) {
            let cursor = event.target.result;
            if (cursor) {
                console.log(`Key: ${cursor.key}, Value: ${cursor.value.value}`);
                cursor.continue();
            }
        };
    });
}

function clearAll() {
    openDB(db => {
        let transaction = db.transaction(STORE_NAME, "readwrite");
        let store = transaction.objectStore(STORE_NAME);
        store.clear();
    });
}

function countEntries(callback) {
    openDB(db => {
        let transaction = db.transaction(STORE_NAME, "readonly");
        let store = transaction.objectStore(STORE_NAME);
        let request = store.count();

        request.onsuccess = function () {
            callback(request.result);
        };
    });
}

console.log("js/indexeddb_manager initialised");

const indexedDBManager = {
    create,
    read,
    remove,
    display,
    clearAll,
    countEntries
};

export { indexedDBManager };

window.indexedDB_manager = indexedDBManager;
