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
* FILE: login.js
* CREATION DATE: 25-01-2026
* LAST Modified: 6:26:42 25-01-2026
* DESCRIPTION: 
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the file that will contain the javascript code to allow the login page to work.
* // AR
* +==== END CatFeeder =================+
*/

function showMessage(elementId, message, isError, timeout) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.color = isError ? "red" : "green";
    if (timeout && isError) {
        setTimeout(() => {
            element.textContent = "";
        }, timeout);
    }
}

function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const script = document.querySelector('script[src*="login.js"]');
    const dashboardUrl = script ? script.dataset.dashboardUrl : "/front-end/dashboard";

    if (window.querier) {
        window.querier.post("/api/v1/login", formData)
            .then(response => {
                if (response.token) {
                    const expires = new Date(Date.now() + 86400000).toUTCString(); // 1 day
                    if (window.cookie_manager) {
                        window.cookie_manager.createCookie("token", response.token, expires, "/");
                    }
                    showMessage("login-message", "Login successful!", false);
                    window.location.href = dashboardUrl;
                } else {
                    showMessage("login-message", "Login failed.", true, 4000);
                }
            })
            .catch(error => {
                showMessage("login-message", "Login error: " + error.message, true, 4000);
            });
    } else {
        showMessage("login-message", "Querier not loaded.", true, 4000);
    }
}

function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const script = document.querySelector('script[src*="login.js"]');
    const dashboardUrl = script ? script.dataset.dashboardUrl : "/front-end/dashboard";

    if (window.querier) {
        window.querier.post("/api/v1/register", formData)
            .then(response => {
                if (response.token) {
                    const expires = new Date(Date.now() + 86400000).toUTCString(); // 1 day
                    if (window.cookie_manager) {
                        window.cookie_manager.createCookie("token", response.token, expires, "/");
                    }
                    showMessage("register-message", "Registration successful! Logging you in.", false);
                    window.location.href = dashboardUrl;
                } else {
                    showMessage("register-message", "Registration failed.", true, 4000);
                }
            })
            .catch(error => {
                showMessage("register-message", "Registration error: " + error.message, true, 4000);
            });
    } else {
        showMessage("register-message", "Querier not loaded.", true, 4000);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const showLoginBtn = document.getElementById("show-login");
    const showRegisterBtn = document.getElementById("show-register");
    const loginSection = document.getElementById("login-section");
    const registerSection = document.getElementById("register-section");

    function showLogin() {
        loginSection.style.display = "block";
        registerSection.style.display = "none";
        showLoginBtn.classList.add("active");
        showRegisterBtn.classList.remove("active");
    }

    function showRegister() {
        loginSection.style.display = "none";
        registerSection.style.display = "block";
        showLoginBtn.classList.remove("active");
        showRegisterBtn.classList.add("active");
    }

    if (showLoginBtn) {
        showLoginBtn.addEventListener("click", showLogin);
    }

    if (showRegisterBtn) {
        showRegisterBtn.addEventListener("click", showRegister);
    }

    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    function togglePasswordVisibility(inputId, button) {
        const input = document.getElementById(inputId);
        if (input.type === "password") {
            input.type = "text";
            button.textContent = "⌣";
            button.setAttribute("aria-label", "Hide password");
        } else {
            input.type = "password";
            button.textContent = "👁";
            button.setAttribute("aria-label", "Show password");
        }
    }

    const toggleLoginPassword = document.getElementById("toggle-login-password");
    if (toggleLoginPassword) {
        toggleLoginPassword.addEventListener("click", () => togglePasswordVisibility("login-password", toggleLoginPassword));
    }

    const toggleRegisterPassword = document.getElementById("toggle-register-password");
    if (toggleRegisterPassword) {
        toggleRegisterPassword.addEventListener("click", () => togglePasswordVisibility("register-password", toggleRegisterPassword));
    }

    // Default to login
    showLogin();
});
