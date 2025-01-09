#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <SPI.h>
#include <MFRC522.h>

// RFID pins
#define RST_PIN D3
#define SS_PIN D4

// WiFi credentials
const char* ssid = "GIHANGA AI";
const char* password = "GIHANGA1";

// Initialize RFID
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Web server on port 80
ESP8266WebServer server(80);

// Store the last read card ID
String lastCardUID = "";
unsigned long lastCardReadTime = 0;

void setup() {
    Serial.begin(9600);
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    
    // Initialize RFID
    SPI.begin();
    mfrc522.PCD_Init();
    
    // Enable CORS
    server.enableCORS(true);

    // Route for getting the last card ID
    server.on("/getcard", HTTP_GET, []() {
        server.send(200, "text/plain", lastCardUID);
    });
    
    // Start server
    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    server.handleClient();
    
    // Check for new cards
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
        String cardUID = "";
        for (byte i = 0; i < mfrc522.uid.size; i++) {
            if (mfrc522.uid.uidByte[i] < 0x10) {
                cardUID += "0";
            }
            cardUID += String(mfrc522.uid.uidByte[i], HEX);
        }
        
        lastCardUID = cardUID;
        lastCardReadTime = millis();
        Serial.println("Card detected: " + cardUID);
        
        mfrc522.PICC_HaltA();
    }
}