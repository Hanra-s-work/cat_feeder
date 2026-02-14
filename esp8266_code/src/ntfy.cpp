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
* LAST Modified: 10:12:51 14-02-2026
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
#include "ntfy.hpp"
#include "config.hpp"
#include "my_overloads.hpp"
#include "shared_dependencies.hpp"

void send_ip_to_ntfy()
{
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;

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
  SharedDependencies::webClient->begin(client, url);
  SharedDependencies::webClient->addHeader("Content-Type", "text/plain");
  SharedDependencies::webClient->addHeader("Title", "ESP8266 Online");
  SharedDependencies::webClient->addHeader("Priority", "3");
  SharedDependencies::webClient->addHeader("Tags", "wifi,esp8266");

  int httpCode = SharedDependencies::webClient->POST((uint8_t *)message, strlen(message));
  SharedDependencies::webClient->end();

  Serial << "ntfy POST result: " << httpCode << endl;
}
