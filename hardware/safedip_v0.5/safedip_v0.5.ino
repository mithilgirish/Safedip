/*
 * Water Quality Monitor
 * ESP32 + DS18B20 + TDS + pH + Turbidity
 * Sends JSON to local Node.js/Python server via HTTP POST
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ════════════════════════════════════════════════════════
//  CONFIG — Edit these
// ════════════════════════════════════════════════════════
const char* WIFI_SSID     = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:3000/api/data";
// Replace IP with your PC's local IP (run `ipconfig` on Windows / `ifconfig` on Mac/Linux)

const char* DEVICE_ID     = "ESP32_WQ_01";
const int   SEND_INTERVAL = 5000; // ms between sends

// ════════════════════════════════════════════════════════
//  PIN DEFINITIONS
// ════════════════════════════════════════════════════════
#define PIN_TDS        34   // Analog (ADC1)
#define PIN_PH         35   // Analog (ADC1)
#define PIN_TURBIDITY  32   // Analog (ADC1)
#define PIN_TEMP        4   // Digital (OneWire)

// ════════════════════════════════════════════════════════
//  CALIBRATION — Adjust after testing with known solutions
// ════════════════════════════════════════════════════════

// --- TDS ---
// Use a known PPM solution to calibrate TDS_FACTOR (default 0.5 works for most generic modules)
#define TDS_FACTOR     0.5f

// --- pH ---
// Step 1: Put probe in pH 7 buffer → note raw voltage → set PH_CAL_V7
// Step 2: Put probe in pH 4 buffer → note raw voltage → set PH_CAL_V4
// Slope and intercept are auto-calculated from these two points
#define PH_CAL_V7      2.50f   // Voltage in pH 7 buffer (measure & replace)
#define PH_CAL_V4      3.05f   // Voltage in pH 4 buffer (measure & replace)

// --- Turbidity ---
// Most generic modules output ~4.1V in clear water, ~0V in very murky water
// Adjust TURB_VOLTAGE_CLEAR if your module differs
#define TURB_VOLTAGE_CLEAR  4.1f

// ════════════════════════════════════════════════════════
//  GLOBALS
// ════════════════════════════════════════════════════════
OneWire           oneWire(PIN_TEMP);
DallasTemperature tempSensor(&oneWire);

const float VREF       = 3.3f;
const int   ADC_RES    = 4096;
const int   AVG_SAMPLES = 15;

unsigned long lastSendTime = 0;

// ════════════════════════════════════════════════════════
//  SETUP
// ════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=== Water Quality Monitor ===");

  // Start temp sensor
  tempSensor.begin();
  Serial.println("[TEMP] DS18B20 initialized");

  // Connect WiFi
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WiFi] FAILED — running in offline mode");
  }
}

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
//  SENSOR READS
// ════════════════════════════════════════════════════════

float readTemperature() {
  tempSensor.requestTemperatures();
  float t = tempSensor.getTempCByIndex(0);
  if (t == DEVICE_DISCONNECTED_C) {
    Serial.println("[TEMP] Sensor disconnected!");
    return -999.0f;
  }
  return t;
}

float readTDS(float tempC) {
  float voltage = toVoltage(analogAvg(PIN_TDS));

  // Temperature compensation (standard formula)
  float tempCoeff = 1.0f + 0.02f * (tempC - 25.0f);
  float compVoltage = voltage / tempCoeff;

  // DFRobot / generic TDS conversion polynomial
  float tds = (133.42f * powf(compVoltage, 3)
             - 255.86f * powf(compVoltage, 2)
             + 857.39f * compVoltage) * TDS_FACTOR;

  return max(tds, 0.0f);
}

float readPH() {
  float voltage = toVoltage(analogAvg(PIN_PH));

  // Two-point linear calibration from pH 4 and pH 7
  float slope     = (7.0f - 4.0f) / (PH_CAL_V7 - PH_CAL_V4);
  float intercept = 7.0f - slope * PH_CAL_V7;
  float ph        = slope * voltage + intercept;

  return constrain(ph, 0.0f, 14.0f);
}

float readTurbidity() {
  float voltage = toVoltage(analogAvg(PIN_TURBIDITY));

  // Generic turbidity sensor — higher voltage = clearer water
  // Clamp to 0–3000 NTU range
  float ntu = (TURB_VOLTAGE_CLEAR - voltage) * 3000.0f / TURB_VOLTAGE_CLEAR;
  return constrain(ntu, 0.0f, 3000.0f);
}

// ════════════════════════════════════════════════════════
//  HTTP POST
// ════════════════════════════════════════════════════════
void sendToServer(float tds, float turbidity, float temp, float ph) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] No WiFi — skipping send");
    return;
  }

  // Build JSON
  StaticJsonDocument<256> doc;
  doc["device_id"]   = DEVICE_ID;
  doc["temperature"] = serialized(String(temp, 2));
  doc["tds"]         = serialized(String(tds, 1));
  doc["turbidity"]   = serialized(String(turbidity, 1));
  doc["ph"]          = serialized(String(ph, 2));
  doc["timestamp"]   = millis();

  String payload;
  serializeJson(doc, payload);

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  int code = http.POST(payload);

  if (code > 0) {
    Serial.printf("[HTTP] %d → %s\n", code, http.getString().c_str());
  } else {
    Serial.printf("[HTTP] Error: %s\n", http.errorToString(code).c_str());
  }

  http.end();
}

// ════════════════════════════════════════════════════════
//  LOOP
// ════════════════════════════════════════════════════════
void loop() {
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();

    float temp      = readTemperature();
    float tds       = readTDS(temp > -100 ? temp : 25.0f); // fallback 25°C if sensor error
    float ph        = readPH();
    float turbidity = readTurbidity();

    // Print to Serial Monitor
    Serial.println("────────────────────────────");
    Serial.printf("  Temp      : %.2f °C\n",  temp);
    Serial.printf("  TDS       : %.1f ppm\n", tds);
    Serial.printf("  pH        : %.2f\n",     ph);
    Serial.printf("  Turbidity : %.1f NTU\n", turbidity);
    Serial.println("────────────────────────────");

    sendToServer(tds, turbidity, temp, ph);
  }
}
