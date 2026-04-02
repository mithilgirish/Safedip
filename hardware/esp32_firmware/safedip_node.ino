/*
 * SafeDip IoT Node — Water Quality Monitor
 * ESP32 + DS18B20 + TDS + pH + Turbidity + ORP
 * Sends JSON to FastAPI backend via HTTP POST
 * 
 * Version: 0.6.0 (Refined from v0.5)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ════════════════════════════════════════════════════════
//  CONFIG — Network & Device
// ════════════════════════════════════════════════════════
const char* WIFI_SSID     = "YOUR_SSID";
const char* WIFI_PASS     = "YOUR_PASSWORD";
const char* API_ENDPOINT  = "http://YOUR_BACKEND_IP:8000/api/v1/ingest";

const char* DEVICE_ID     = "ESP32_01";
const char* POOL_ID       = "pool_vit_01";
const int   SEND_INTERVAL = 5000; // ms between sends

// ════════════════════════════════════════════════════════
//  PIN DEFINITIONS
// ════════════════════════════════════════════════════════
#define PIN_PH         34   // Analog (ADC1)
#define PIN_TDS        35   // Analog (ADC1)
#define PIN_TURB       32   // Analog (ADC1)
#define PIN_ORP        33   // Analog (ADC1)
#define PIN_TEMP        4   // Digital (OneWire)

// ════════════════════════════════════════════════════════
//  CALIBRATION & CONSTANTS
// ════════════════════════════════════════════════════════

// --- TDS ---
#define TDS_FACTOR     0.5f

// --- pH ---
#define PH_CAL_V7      2.50f   // Voltage in pH 7 buffer
#define PH_CAL_V4      3.05f   // Voltage in pH 4 buffer

// --- Turbidity ---
#define TURB_VOLT_CLEAR 4.1f   // Voltage in clear water

// --- ORP ---
#define ORP_OFFSET     0       // Calibration offset in mV

const float VREF       = 3.3f;
const int   ADC_RES    = 4096;
const int   AVG_SAMPLES = 15;

// ════════════════════════════════════════════════════════
//  GLOBALS
// ════════════════════════════════════════════════════════
OneWire           oneWire(PIN_TEMP);
DallasTemperature tempSensor(&oneWire);

unsigned long lastSendTime = 0;

// ════════════════════════════════════════════════════════
//  HELPERS
// ════════════════════════════════════════════════════════

// Average multiple ADC reads to reduce noise
float analogAvg(int pin) {
  long sum = 0;
  for (int i = 0; i < AVG_SAMPLES; i++) {
    sum += analogRead(pin);
    delay(5);
  }
  return (float)sum / AVG_SAMPLES;
}

// ADC raw → Voltage
float toVoltage(float raw) {
  return raw * VREF / (float)ADC_RES;
}

// ════════════════════════════════════════════════════════
//  SENSOR READINGS
// ════════════════════════════════════════════════════════

float readTemperature() {
  tempSensor.requestTemperatures();
  float t = tempSensor.getTempCByIndex(0);
  if (t == DEVICE_DISCONNECTED_C) {
    Serial.println("[TEMP] Sensor DISCONNECTED!");
    return -999.0f;
  }
  return t;
}

float readTDS(float tempC) {
  float voltage = toVoltage(analogAvg(PIN_TDS));
  
  // Temperature compensation
  float tempCoeff = 1.0f + 0.02f * (tempC - 25.0f);
  float compVoltage = voltage / tempCoeff;

  // DFRobot TDS polynomial
  float tds = (133.42f * powf(compVoltage, 3)
             - 255.86f * powf(compVoltage, 2)
             + 857.39f * compVoltage) * TDS_FACTOR;

  return max(tds, 0.0f);
}

float readPH() {
  float voltage = toVoltage(analogAvg(PIN_PH));
  
  // Two-point linear calibration
  float slope     = (7.0f - 4.0f) / (PH_CAL_V7 - PH_CAL_V4);
  float intercept = 7.0f - slope * PH_CAL_V7;
  float ph        = slope * voltage + intercept;

  return constrain(ph, 0.0f, 14.0f);
}

float readTurbidity() {
  float voltage = toVoltage(analogAvg(PIN_TURB));
  
  // NTU Approximation (Higher voltage = Clearer water)
  float ntu = (TURB_VOLT_CLEAR - voltage) * 3000.0f / TURB_VOLT_CLEAR;
  return constrain(ntu, 0.0f, 3000.0f);
}

float readORP() {
  float voltage = toVoltage(analogAvg(PIN_ORP));
  
  // Standard ORP formula: maps voltage to mV
  // Usually probe range is -2000 to +2000 mV
  // Adjust based on your specific module mapping
  float orp = (voltage - (VREF / 2.0f)) * 1000.0f + ORP_OFFSET;
  return orp;
}

// ════════════════════════════════════════════════════════
//  NETWORKING
// ════════════════════════════════════════════════════════

void sendToServer(float temp, float tds, float ph, float turb, float orp) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] No WiFi connection — skipping");
    return;
  }

  // Use DynamicJsonDocument for payload
  StaticJsonDocument<512> doc;
  doc["device_id"]   = DEVICE_ID;
  doc["pool_id"]     = POOL_ID;
  doc["temperature"] = serialized(String(temp, 2));
  doc["tds"]         = serialized(String(tds, 1));
  doc["ph"]          = serialized(String(ph, 2));
  doc["turbidity"]   = serialized(String(turb, 1));
  doc["orp"]         = serialized(String(orp, 1));
  doc["timestamp"]   = millis();

  String payload;
  serializeJson(doc, payload);

  HTTPClient http;
  http.begin(API_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  
  int code = http.POST(payload);

  if (code > 0) {
    Serial.printf("[HTTP] Success (%d): %s\n", code, http.getString().c_str());
  } else {
    Serial.printf("[HTTP] Error: %s\n", http.errorToString(code).c_str());
  }

  http.end();
}

// ════════════════════════════════════════════════════════
//  SETUP & LOOP
// ════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== SafeDip IoT Node v0.6 ===");

  // Init Sensors
  tempSensor.begin();
  Serial.println("[INIT] DS18B20 Temp sensor ready");

  // WiFi Setup
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 40) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WiFi] FAILED — Running in offline/debug mode");
  }
}

void loop() {
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();

    float temp = readTemperature();
    // Use fallback 25C for TDS if temp sensor fails
    float tds  = readTDS(temp > -50 ? temp : 25.0f);
    float ph   = readPH();
    float turb = readTurbidity();
    float orp  = readORP();

    // Debugging output
    Serial.println("────────────────────────────");
    Serial.printf(" Device: %s | Pool: %s\n", DEVICE_ID, POOL_ID);
    Serial.printf("  Temp      : %.2f °C\n",  temp);
    Serial.printf("  TDS       : %.1f ppm\n", tds);
    Serial.printf("  pH        : %.2f\n",     ph);
    Serial.printf("  Turbidity : %.1f NTU\n", turb);
    Serial.printf("  ORP       : %.1f mV\n",  orp);
    Serial.println("────────────────────────────");

    sendToServer(temp, tds, ph, turb, orp);
  }
}
