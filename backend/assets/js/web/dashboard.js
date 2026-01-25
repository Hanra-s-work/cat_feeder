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
* LAST Modified: 1:19:15 25-01-2026
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
    window.location.href = logoutUrl;
}
