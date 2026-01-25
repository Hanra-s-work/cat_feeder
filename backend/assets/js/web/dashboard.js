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
* LAST Modified: 7:8:34 25-01-2026
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
        if (response.ok && response.data.feeders) {
            displayFeeders(response.data.feeders);
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
        if (response.ok && response.data.beacons) {
            displayBeacons(response.data.beacons);
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
        if (response.ok && response.data.pets) {
            displayPets(response.data.pets);
        } else {
            showMessage("Failed to load pets", true);
        }
    } catch (error) {
        showMessage("Error loading pets: " + error.message, true);
    }
}

function displayFeeders(feeders) {
    const list = document.getElementById("feeders-list");
    list.innerHTML = "";
    feeders.forEach(feeder => {
        const item = document.createElement("li");
        item.textContent = `${feeder.name} - ${feeder.city_locality}, ${feeder.country}`;
        list.appendChild(item);
    });
}

function displayBeacons(beacons) {
    const list = document.getElementById("beacons-list");
    list.innerHTML = "";
    beacons.forEach(beacon => {
        const item = document.createElement("li");
        item.textContent = `${beacon.name} - ${beacon.city_locality}, ${beacon.country}`;
        list.appendChild(item);
    });
}

function displayPets(pets) {
    const list = document.getElementById("pets-list");
    list.innerHTML = "";
    pets.forEach(pet => {
        const item = document.createElement("li");
        item.textContent = `${pet.name} - ${pet.breed}, ${pet.age} years old`;
        list.appendChild(item);
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
        const formData = {
            name: document.getElementById("feeder-name").value,
            mac: document.getElementById("feeder-mac").value,
            latitude: parseFloat(document.getElementById("feeder-latitude").value),
            longitude: parseFloat(document.getElementById("feeder-longitude").value),
            city_locality: document.getElementById("feeder-city").value,
            country: document.getElementById("feeder-country").value
        };

        try {
            const response = await window.querier.put('/api/v1/feeder', formData);
            if (response.ok) {
                showMessage("Feeder registered successfully!");
                feederForm.style.display = "none";
                registerFeederForm.reset();
            } else {
                showMessage("Failed to register feeder: " + (response.message || "Unknown error"), true);
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
            const response = await window.querier.get(`/api/v1/feeder/${name}/status`);
            if (response.ok) {
                const status = response.data;
                showMessage(`Feeder ${name} status: ${JSON.stringify(status)}`);
            } else {
                showMessage("Failed to get feeder status: " + (response.message || "Unknown error"), true);
            }
        } catch (error) {
            showMessage("Error getting feeder status: " + error.message, true);
        }
    });

    // Feed action
    const feedForm = document.getElementById("feed-form");
    feedForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("feed-feeder-name").value;
        const amount = parseInt(document.getElementById("feed-amount").value);
        try {
            const response = await window.querier.post(`/api/v1/feeder/${name}/feed`, { amount });
            if (response.ok) {
                showMessage("Feeding successful!");
            } else {
                showMessage("Failed to feed: " + (response.message || "Unknown error"), true);
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
        const formData = {
            name: document.getElementById("beacon-name").value,
            mac: document.getElementById("beacon-mac").value,
            latitude: parseFloat(document.getElementById("beacon-latitude").value),
            longitude: parseFloat(document.getElementById("beacon-longitude").value),
            city_locality: document.getElementById("beacon-city").value,
            country: document.getElementById("beacon-country").value
        };

        try {
            const response = await window.querier.put('/api/v1/beacon', formData);
            if (response.ok) {
                showMessage("Beacon registered successfully!");
                beaconForm.style.display = "none";
                registerBeaconForm.reset();
            } else {
                showMessage("Failed to register beacon: " + (response.message || "Unknown error"), true);
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
            const response = await window.querier.get(`/api/v1/beacon/${name}/status`);
            if (response.ok) {
                const status = response.data;
                showMessage(`Beacon ${name} status: ${JSON.stringify(status)}`);
            } else {
                showMessage("Failed to get beacon status: " + (response.message || "Unknown error"), true);
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
        const formData = {
            name: document.getElementById("pet-name").value,
            breed: document.getElementById("pet-breed").value,
            age: parseInt(document.getElementById("pet-age").value),
            weight: parseFloat(document.getElementById("pet-weight").value),
            color: document.getElementById("pet-color").value,
            microchip_id: document.getElementById("pet-microchip").value
        };

        try {
            const response = await window.querier.put('/api/v1/pet', formData);
            if (response.ok) {
                showMessage("Pet registered successfully!");
                petForm.style.display = "none";
                registerPetForm.reset();
            } else {
                showMessage("Failed to register pet: " + (response.message || "Unknown error"), true);
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
            const response = await window.querier.get(`/api/v1/pet/${id}`);
            if (response.ok) {
                const pet = response.data;
                showMessage(`Pet info: ${JSON.stringify(pet)}`);
            } else {
                showMessage("Failed to get pet info: " + (response.message || "Unknown error"), true);
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
    loadFeeders(token);
    loadBeacons(token);
    loadPets(token);

    setupFeederForm();
    setupBeaconForm();
    setupPetForm();
});
