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
* FILE: logout.js
* CREATION DATE: 25-01-2026
* LAST Modified: 4:23:19 25-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the javascript code that will allow the logout page to work.
* // AR
* +==== END CatFeeder =================+
*/

const script = document.querySelector('script[src*="logout.js"]');
const loginUrl = script ? script.dataset.loginUrl : "/front-end/";

document.addEventListener("DOMContentLoaded", async function () {
    const messageDiv = document.getElementById("logout-message");
    const retryButton = document.getElementById("retry-logout");
    const backButton = document.getElementById("back-to-login");

    const token = window.cookie_manager.read('token');

    async function attemptLogout() {
        if (!token) {
            messageDiv.textContent = "No active session found.";
            backButton.style.display = "block";
            return;
        }

        try {
            const logoutResponse = await window.querier.post('/api/v1/logout', {}, token);
            if (logoutResponse.ok || logoutResponse.status === 401) {
                // Logout succeeded or already logged out (401)
                const validResponse = await window.querier.get('/api/v1/token/valid', {}, token);
                if (!validResponse.ok) {
                    messageDiv.textContent = logoutResponse.status === 401 ? "You are already logged out." : "You have been logged out successfully.";
                    window.cookie_manager.remove('token');
                    backButton.style.display = "block";
                } else {
                    messageDiv.textContent = "Logout request sent, but token may still be valid. Please try again.";
                    retryButton.style.display = "block";
                    backButton.style.display = "block";
                }
            } else {
                messageDiv.textContent = "Logout failed: " + (logoutResponse.message || "Unknown error");
                retryButton.style.display = "block";
                backButton.style.display = "block";
            }
        } catch (error) {
            messageDiv.textContent = "Logout failed: Network error";
            retryButton.style.display = "block";
            backButton.style.display = "block";
        }
    }

    // Initial attempt
    await attemptLogout();

    retryButton.addEventListener("click", async function () {
        retryButton.style.display = "none";
        messageDiv.textContent = "Processing logout...";
        await attemptLogout();
    });

    backButton.addEventListener("click", function () {
        window.location.href = loginUrl;
    });
});
