#include "WifiCam.hpp"      // Biblioteca personalizada para ESP32-CAM
#include "NetworkModel.hpp" // Estrutura que guarda dados de redes Wi-Fi
#include <WiFi.h>           // Biblioteca oficial do ESP32 para Wi-Fi

// Objeto para armazenar a resolução inicial da câmera
esp32cam::Resolution initialResolution;

// Servidor web rodando na porta 80
WebServer server(80);

// ======================
// Definir redes Wi-Fi disponíveis
// ======================
NetworkModel networks[] = {
    NetworkModel("FamiliaBuscape", "Elephant33", IPAddress(192,168,0,20), IPAddress(192,168,0,1), IPAddress(255,255,255,0)),
    NetworkModel("OTHER_WIFI", "OtherPass", IPAddress(0,0,0,0), IPAddress(0,0,0,0), IPAddress(0,0,0,0)) // rede com DHCP
};

// Quantidade de redes definidas
const int networkCount = sizeof(networks)/sizeof(networks[0]);

// ======================
// Função que conecta a uma rede Wi-Fi
// ======================
bool connectToWiFi(NetworkModel net, int timeout = 10000) {
  WiFi.disconnect();       // Desconecta de qualquer rede existente
  WiFi.mode(WIFI_STA);     // Configura o ESP32 como cliente Wi-Fi

  // Configura IP fixo somente se não for 0.0.0.0
  if (net.ip != IPAddress(0,0,0,0)) {
    WiFi.config(net.ip, net.gateway, net.subnet);
  }

  // Inicia a conexão Wi-Fi
  WiFi.begin(net.ssid, net.password);
  Serial.printf("Connecting to WiFi: %s...\n", net.ssid);

  // Aguarda até conectar ou até atingir o timeout
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < timeout) {
    delay(500);
    Serial.print("."); // Mostra progresso no monitor serial
  }
  Serial.println();

  // Verifica se conseguiu conectar
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("Connected to %s with IP: %s\n", net.ssid, WiFi.localIP().toString().c_str());
    return true;
  } else {
    Serial.printf("Failed to connect to %s\n", net.ssid);
    return false;
  }
}

// ======================
// Função setup() - executada uma vez na inicialização
// ======================
void setup() {
  Serial.begin(115200); // Inicializa comunicação serial para debug
  delay(1000);

  pinMode(FLASH_PIN, OUTPUT); // Configura o LED da câmera
  digitalWrite(FLASH_PIN, 0); // Apaga o LED inicialmente

  // ======================
  // Tenta conectar a cada rede do array
  // ======================
  bool connected = false;
  for (int i = 0; i < networkCount; i++) {
    if (connectToWiFi(networks[i], 10000)) { // Timeout 10s
      connected = true;
      break; // Sai do loop se conectar com sucesso
    }
  }

  // Se nenhuma rede funcionar, reinicia o ESP32
  if (!connected) {
    Serial.println("All WiFi connection attempts failed. Restarting...");
    delay(5000);
    ESP.restart();
  }

  // ======================
  // Inicialização da câmera
  // ======================
  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768); // Define resolução da câmera

    Config cfg;               // Objeto de configuração da câmera
    cfg.setPins(pins::AiThinker); // Define os pinos do módulo Ai-Thinker
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);          // Qualidade da imagem JPEG (0-100)

    bool ok = Camera.begin(cfg); // Inicializa a câmera
    if (!ok) {
      Serial.println("Camera initialization failed"); // Falha na inicialização
      delay(5000);
      ESP.restart();
    }
    Serial.println("Camera initialized successfully"); // Sucesso
  }

  // Mostra no serial o IP da câmera
  Serial.printf("Camera ready at http://%s\n", WiFi.localIP().toString().c_str());

  addRequestHandlers(); // Função externa que adiciona rotas HTTP
  server.begin();       // Inicia servidor web
}

// ======================
// Função loop() - executada continuamente
// ======================
void loop() {
  server.handleClient(); // Mantém servidor web ativo e processa requisições
}
