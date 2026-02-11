/*
* +==== BEGIN CatFeeder =================+
* LOGO:
* ..............(....⁄\
* ...............)..(.')
* ..............(../..)
* ...............\(__)|
* Inspired by Joan Stark
* source https://www.asciiart.eu/
* animals/cats
* /STOP
* PROJECT: CatFeeder
* FILE: ntfy.cpp
* CREATION DATE: 07-02-2026
* LAST Modified: 23:30:12 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the ntfy implementation.
* // AR
* +==== END CatFeeder =================+
*/
#include <cstdio>
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "my_overloads.hpp"
#include "config.hpp"
#include "ntfy.hpp"

void send_ip_to_ntfy()
{
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;
  HTTPClient http;

  // ---- Build URL ----
  constexpr unsigned int url_size = (sizeof(NTFY_SERVER) - 1) + 1 + (sizeof(NTFY_TOPIC) - 1) + 1;
  char url[url_size];
  snprintf(url, sizeof(url), "%s/%s", NTFY_SERVER, NTFY_TOPIC);

  // ---- Convert IP to string without using String ----
  IPAddress ip = WiFi.localIP();

  char ipStr[16];  // Max "255.255.255.255" + null
  snprintf(ipStr, sizeof(ipStr), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);

  // ---- Build message ----
  char message[128];  // adjust if needed

  snprintf(message, sizeof(message), "ESP8266 IP: %s\nName: %s", ipStr, BOARD_NAME);

  // ---- Send HTTP ----
  http.begin(client, url);
  http.addHeader("Content-Type", "text/plain");
  http.addHeader("Title", "ESP8266 Online");
  http.addHeader("Priority", "3");
  http.addHeader("Tags", "wifi,esp8266");

  int httpCode = http.POST((uint8_t *)message, strlen(message));
  http.end();

  Serial << "ntfy POST result: " << httpCode << endl;
}
