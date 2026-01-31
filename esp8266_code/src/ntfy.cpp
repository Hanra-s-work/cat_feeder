#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "config.hpp"
#include "ntfy.hpp"

void send_ip_to_ntfy()
{
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;
  HTTPClient http;

  String url = String(NTFY_SERVER) + "/" + NTFY_TOPIC;
  String message = "ESP8266 IP: " + WiFi.localIP().toString() + "<br>Name: " + BOARD_NAME;

  http.begin(client, url);
  http.addHeader("Content-Type", "text/plain");
  http.addHeader("Title", "ESP8266 Online");
  http.addHeader("Priority", "3");
  http.addHeader("Tags", "wifi,esp8266");

  int httpCode = http.POST(message);
  http.end();

  Serial.print("ntfy POST result: ");
  Serial.println(httpCode);
}
