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
* FILE: dashboard.js
* CREATION DATE: 25-01-2026
* LAST Modified: 17:4:26 31-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the javascript file that aims to contain the javascript function that will be run be the dashboard page.
* // AR
* +==== END CatFeeder =================+
*/

const script = document.querySelector('script[src*="dashboard.js"]');
const loginUrl = script ? script.dataset.loginUrl : "/front-end/";
const logoutUrl = script ? script.dataset.logoutUrl : "/front-end/logout";

// ---------- MAC address helpers ----------
function _cleanMacRaw(s) {
    if (!s || typeof s !== 'string') return '';
    return s.toUpperCase().replace(/[^0-9A-F]/g, '');
}

function normalizeMac(input) {
    // Accept input with separators or without, return uppercase colon-separated pairs
    const raw = _cleanMacRaw(input);
    if (raw.length === 12) {
        return raw.match(/.{1,2}/g).join(':');
    }
    if (raw.length === 8) {
        // allow 4-byte MACs (rare) - format as 4 pairs
        return raw.match(/.{1,2}/g).join(':');
    }
    return null;
}

function validateMac(input) {
    const norm = normalizeMac(input);
    if (!norm) return false;
    // basic validation - pairs of hex separated by colon, 4 or 6 pairs
    return /^([0-9A-F]{2}:){3,5}[0-9A-F]{2}$/.test(norm);
}

function attachMacBlurFormatting(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.setAttribute('placeholder', 'AA:BB:CC:DD:EE:FF');
    el.setAttribute('maxlength', '17');
    el.addEventListener('blur', () => {
        const v = el.value || '';
        const norm = normalizeMac(v);
        if (norm) el.value = norm;
    });
}


function logout() {
    const logoutUrlFull = logoutUrl;
    window.location.href = logoutUrlFull;
}

function showMessage(message, isError = false) {
    const messageDiv = document.getElementById("message");
    messageDiv.textContent = message;
    messageDiv.style.color = isError ? "red" : "green";
    setTimeout(() => messageDiv.textContent = "", 5000);
}

async function loadFeeders(token) {
    try {
        const response = await window.querier.get('/api/v1/feeders', {}, token);
        if (response.ok) {
            const feeders = response.resp || [];
            if (Array.isArray(feeders)) {
                displayFeeders(feeders);
            } else {
                showMessage("Failed to load feeders", true);
            }
        } else {
            showMessage("Failed to load feeders", true);
        }
    } catch (error) {
        showMessage("Error loading feeders: " + error.message, true);
    }
}

async function loadBeacons(token) {
    try {
        const response = await window.querier.get('/api/v1/beacons', {}, token);
        if (response.ok) {
            const beacons = response.resp || [];
            if (Array.isArray(beacons)) {
                displayBeacons(beacons);
            } else {
                showMessage("Failed to load beacons", true);
            }
        } else {
            showMessage("Failed to load beacons", true);
        }
    } catch (error) {
        showMessage("Error loading beacons: " + error.message, true);
    }
}

async function loadPets(token) {
    try {
        const response = await window.querier.get('/api/v1/pets', {}, token);
        if (response.ok) {
            const pets = response.resp || [];
            if (Array.isArray(pets)) {
                displayPets(pets);
            } else {
                showMessage("Failed to load pets", true);
            }
        } else {
            showMessage("Failed to load pets", true);
        }
    } catch (error) {
        showMessage("Error loading pets: " + error.message, true);
    }
}

function displayFeeders(feeders) {
    const tbody = document.getElementById("feeders-list");
    tbody.innerHTML = "";
    if (feeders.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.setAttribute("colspan", "5");
        cell.style.textAlign = "center";
        cell.textContent = "No feeders found";
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    feeders.forEach(feeder => {
        const row = document.createElement("tr");
        
        // Based on actual API response structure
        const name = feeder.owner || feeder.name || 'Unnamed';
        const mac = feeder.latitude || feeder.mac || 'No MAC';
        const city = feeder.country || feeder.city_locality || 'Unknown City';
        const country = feeder.mac || feeder.country || 'Unknown Country';
        const lat = feeder.longitude || 'N/A';
        const lon = feeder.city_locality || 'N/A';
        
        row.innerHTML = `
            <td>${feeder.id}</td>
            <td>${name}</td>
            <td>${mac}</td>
            <td>${city}, ${country}</td>
            <td>${lat}, ${lon}</td>
        `;
        tbody.appendChild(row);
    });
}

function displayBeacons(beacons) {
    const tbody = document.getElementById("beacons-list");
    tbody.innerHTML = "";
    if (beacons.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.setAttribute("colspan", "3");
        cell.style.textAlign = "center";
        cell.textContent = "No beacons found";
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    beacons.forEach(beacon => {
        const row = document.createElement("tr");
        
        // Based on actual API response structure
        const name = beacon.owner || beacon.name || 'Unnamed';
        const mac = beacon.mac || 'No MAC';
        
        row.innerHTML = `
            <td>${beacon.id}</td>
            <td>${name}</td>
            <td>${mac}</td>
        `;
        tbody.appendChild(row);
    });
}

function displayPets(pets) {
    const tbody = document.getElementById("pets-list");
    tbody.innerHTML = "";
    if (pets.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.setAttribute("colspan", "5");
        cell.style.textAlign = "center";
        cell.textContent = "No pets found";
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    pets.forEach(pet => {
        const row = document.createElement("tr");
        
        const name = pet.name || 'Unnamed';
        const breed = pet.breed || 'Unknown breed';
        const age = pet.age !== undefined ? pet.age : 'Unknown';
        const weight = pet.weight !== undefined ? pet.weight : 'N/A';
        
        row.innerHTML = `
            <td>${pet.id}</td>
            <td>${name}</td>
            <td>${breed}</td>
            <td>${age}</td>
            <td>${weight}</td>
        `;
        tbody.appendChild(row);
    });
}

function setupFeederForm() {
    const addFeederBtn = document.getElementById("add-feeder");
    const feederForm = document.getElementById("feeder-form");
    const registerFeederForm = document.getElementById("register-feeder-form");
    const cancelFeederBtn = document.getElementById("cancel-feeder");

    addFeederBtn.addEventListener("click", () => {
        feederForm.style.display = "block";
    });

    cancelFeederBtn.addEventListener("click", () => {
        feederForm.style.display = "none";
        registerFeederForm.reset();
    });

    registerFeederForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        // validate and normalize MAC
        const feederMacRaw = document.getElementById("feeder-mac").value;
        const feederMac = normalizeMac(feederMacRaw);
        if (!feederMac) {
            showMessage('Invalid feeder MAC address', true);
            return;
        }

        const formData = {
            name: document.getElementById("feeder-name").value,
            mac: feederMac,
            latitude: parseFloat(document.getElementById("feeder-latitude").value),
            longitude: parseFloat(document.getElementById("feeder-longitude").value),
            city_locality: document.getElementById("feeder-city").value,
            country: document.getElementById("feeder-country").value
        };

        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.put('/api/v1/feeder', formData, token);
            if (response.ok) {
                showMessage(response.msg || "Feeder registered successfully!");
                feederForm.style.display = "none";
                registerFeederForm.reset();
                loadFeeders(token);
            } else {
                showMessage("Failed to register feeder: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error registering feeder: " + error.message, true);
        }
    });

    // Feeder status check
    const checkFeederStatusForm = document.getElementById("check-feeder-status-form");
    checkFeederStatusForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("check-feeder-name").value;
        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.get('/api/v1/feeder/status', { name }, token);
            if (response.ok) {
                const status = response.resp || response.msg || response;
                showMessage(`Feeder ${name} status: ${JSON.stringify(status)}`);
            } else {
                showMessage("Failed to get feeder status: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error getting feeder status: " + error.message, true);
        }
    });

    // Feed action
    const feedForm = document.getElementById("feed-form");
    feedForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const feeder_mac = document.getElementById("feed-feeder-mac").value;
        const beacon_mac = document.getElementById("feed-beacon-mac").value;
        const amount = parseInt(document.getElementById("feed-amount").value);
        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.post('/api/v1/feeder/fed', { feeder_mac, beacon_mac, amount }, token);
            if (response.ok) {
                showMessage(response.msg || "Feeding successful!");
            } else {
                showMessage("Failed to feed: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error feeding: " + error.message, true);
        }
    });
}

function setupBeaconForm() {
    const addBeaconBtn = document.getElementById("add-beacon");
    const beaconForm = document.getElementById("beacon-form");
    const registerBeaconForm = document.getElementById("register-beacon-form");
    const cancelBeaconBtn = document.getElementById("cancel-beacon");

    addBeaconBtn.addEventListener("click", () => {
        beaconForm.style.display = "block";
    });

    cancelBeaconBtn.addEventListener("click", () => {
        beaconForm.style.display = "none";
        registerBeaconForm.reset();
    });

    registerBeaconForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const beaconMacRaw = document.getElementById("beacon-mac").value;
        const beaconMac = normalizeMac(beaconMacRaw);
        if (!beaconMac) {
            showMessage('Invalid beacon MAC address', true);
            return;
        }

        const formData = {
            name: document.getElementById("beacon-name").value,
            mac: beaconMac
        };

        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.put('/api/v1/feeder/beacon', formData, token);
            if (response.ok) {
                showMessage(response.msg || "Beacon registered successfully!");
                beaconForm.style.display = "none";
                registerBeaconForm.reset();
                loadBeacons(token);
            } else {
                showMessage("Failed to register beacon: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error registering beacon: " + error.message, true);
        }
    });

    // Beacon status check
    const checkBeaconStatusForm = document.getElementById("check-beacon-status-form");
    checkBeaconStatusForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("check-beacon-name").value;
        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.get('/api/v1/feeder/beacon/status', { name }, token);
            if (response.ok) {
                const status = response.resp || response.msg || response;
                showMessage(`Beacon ${name} status: ${JSON.stringify(status)}`);
            } else {
                showMessage("Failed to get beacon status: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error getting beacon status: " + error.message, true);
        }
    });
}

function setupPetForm() {
    const addPetBtn = document.getElementById("add-pet");
    const petForm = document.getElementById("pet-form");
    const registerPetForm = document.getElementById("register-pet-form");
    const cancelPetBtn = document.getElementById("cancel-pet");

    addPetBtn.addEventListener("click", () => {
        petForm.style.display = "block";
    });

    cancelPetBtn.addEventListener("click", () => {
        petForm.style.display = "none";
        registerPetForm.reset();
    });

    registerPetForm.addEventListener("submit", async (e) => {
        e.preventDefault();
            const petBeaconRaw = document.getElementById("pet-beacon-mac").value;
            const petBeaconMac = normalizeMac(petBeaconRaw);
            if (!petBeaconMac) {
                showMessage('Invalid pet beacon MAC address', true);
                return;
            }

            const formData = {
                beacon_mac: petBeaconMac,
                name: document.getElementById("pet-name").value,
                breed: document.getElementById("pet-breed").value,
                age: parseInt(document.getElementById("pet-age").value),
                weight: parseFloat(document.getElementById("pet-weight").value),
                microchip_id: document.getElementById("pet-microchip").value
            };

        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.put('/api/v1/pet', formData, token);
            if (response.ok) {
                showMessage(response.msg || "Pet registered successfully!");
                petForm.style.display = "none";
                registerPetForm.reset();
                loadPets(token);
            } else {
                showMessage("Failed to register pet: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error registering pet: " + error.message, true);
        }
    });

    // Get pet info
    const getPetForm = document.getElementById("get-pet-form");
    getPetForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("get-pet-id").value;
        try {
            const token = (window.cookie_manager && window.cookie_manager.readCookie) ? window.cookie_manager.readCookie("token") : "";
            const response = await window.querier.get('/api/v1/pet', { id }, token);
            if (response.ok) {
                const pet = response.resp || response;
                showMessage(`Pet info: ${JSON.stringify(pet)}`);
            } else {
                showMessage("Failed to get pet info: " + (response.msg || response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error getting pet info: " + error.message, true);
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // Check if modules are loaded
    if (!window.querier) {
        console.error("Querier module not loaded");
        showMessage("Error: Required modules not loaded. Please refresh the page.", true);
        return;
    }
    if (!window.cookie_manager) {
        console.error("Cookie manager module not loaded");
        showMessage("Error: Required modules not loaded. Please refresh the page.", true);
        return;
    }

    const token = window.cookie_manager.readCookie("token") ?? "";

    // attach MAC formatting/validation to inputs
    attachMacBlurFormatting('feeder-mac');
    attachMacBlurFormatting('beacon-mac');
    attachMacBlurFormatting('pet-beacon-mac');
    attachMacBlurFormatting('feed-feeder-mac');
    attachMacBlurFormatting('feed-beacon-mac');

    loadFeeders(token);
    loadBeacons(token);
    loadPets(token);

    setupFeederForm();
    setupBeaconForm();
    setupPetForm();

    // Setup refresh buttons
    document.getElementById("refresh-feeders").addEventListener("click", () => {
        const token = window.cookie_manager.readCookie("token") ?? "";
        loadFeeders(token);
        showMessage("Feeders refreshed");
    });

    document.getElementById("refresh-beacons").addEventListener("click", () => {
        const token = window.cookie_manager.readCookie("token") ?? "";
        loadBeacons(token);
        showMessage("Beacons refreshed");
    });

    document.getElementById("refresh-pets").addEventListener("click", () => {
        const token = window.cookie_manager.readCookie("token") ?? "";
        loadPets(token);
        showMessage("Pets refreshed");
    });
});
