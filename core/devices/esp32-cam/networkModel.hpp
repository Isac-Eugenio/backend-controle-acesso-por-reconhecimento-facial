#ifndef NETWORK_MODEL_HPP  // Proteção contra múltiplos includes
#define NETWORK_MODEL_HPP

#include <Arduino.h>  // Biblioteca base do Arduino, necessária para tipos como String
#include <WiFi.h>     // Biblioteca do ESP32 para IPAddress e configuração de Wi-Fi

// ======================
// Estrutura para armazenar dados de uma rede Wi-Fi
// ======================
struct NetworkModel {
  String ssid;     // Nome da rede Wi-Fi (SSID)
  String password; // Senha da rede Wi-Fi
  IPAddress ip;    // Endereço IP fixo (se for usar DHCP, pode ser 0.0.0.0)
  IPAddress gateway;// Gateway da rede
  IPAddress subnet; // Máscara de sub-rede

  // ======================
  // Construtor da estrutura
  // ======================
  // Recebe SSID, senha, IP, gateway e subnet e inicializa os membros
  NetworkModel(const char* ssid_,
               const char* password_,
               IPAddress ip_,
               IPAddress gateway_,
               IPAddress subnet_)
    : ssid(ssid_),           // Inicializa ssid a partir de const char*
      password(password_),   // Inicializa password a partir de const char*
      ip(ip_),               // Inicializa IP
      gateway(gateway_),     // Inicializa gateway
      subnet(subnet_) {}     // Inicializa subnet
};

#endif // Fim da proteção contra múltiplos includes
