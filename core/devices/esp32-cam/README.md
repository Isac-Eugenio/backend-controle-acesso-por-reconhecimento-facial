# 📸 Webserver ESP32-CAM para Controle de Acesso

Este exemplo roda na **placa ESP32-CAM Ai-Thinker** e utiliza a biblioteca [ESP32-CAM do Yoursunny](https://github.com/Yoursunny/esp32cam) para criar um **servidor HTTP** que permite acessar imagens nos formatos **BMP**, **JPG** e **MJPEG** em várias resoluções.

---

## ⚙️ Funcionamento

- O ESP32 cria um **servidor HTTP** acessível via navegador.
- Você pode visualizar fotos ou streams em diferentes resoluções.
- ⚠️ Atenção: o ESP32 `WebServer` suporta **apenas uma conexão TCP por vez**.
  - Se estiver acessando um stream MJPEG no navegador, clique no botão *Stop* para liberar a conexão.
  - Caso contrário, não será possível abrir outra página ou visualizar outra imagem até liberar a conexão.

---


## 📝 Observações importantes

| Item | Detalhes |
|------|----------|
| **Formato BMP** | Não recomendado em alta resolução devido à memória limitada do ESP32-CAM. |
| **Wi-Fi** | Modifique o SSID e a senha da sua rede antes de enviar o código. |
| **Biblioteca** | Este exemplo usa a biblioteca ESP32-CAM desenvolvida por **Yoursunny**. |
| **Hardware** | Módulo **Ai-Thinker**, com pinos configurados corretamente. |

---

## ⚡ Configuração de redes Wi-Fi

O código principal do projeto está em:  

```
ESP32-CAM_CONTROLE_WEBCAM.ino
````

### Passos para modificar ou adicionar redes:

1. Abra o arquivo `.ino` no **Arduino IDE**.  
2. Localize o **array de redes Wi-Fi** (`NetworkModel networks[]`).  
3. Você pode:
   - Modificar as redes existentes alterando SSID, senha, IP, gateway e subnet.  
   - Adicionar novas redes criando novos elementos no array, seguindo o mesmo formato:

```cpp
NetworkModel networks[] = {
    NetworkModel("Rede1", "Senha1", IPAddress(192,168,0,20), IPAddress(192,168,0,1), IPAddress(255,255,255,0)),
    NetworkModel("Rede2", "Senha2", IPAddress(0,0,0,0), IPAddress(0,0,0,0), IPAddress(0,0,0,0)) // sem IP fixo (DHCP)
};
````

4. Salve o arquivo após fazer as alterações.

### Upload para o ESP32-CAM:

* No **Arduino IDE**, selecione a **placa ESP32-CAM Ai-Thinker** e a **porta serial correta**.
* Clique em **Upload** para enviar o código para o ESP32-CAM.
* Abra o **Monitor Serial** para verificar se a conexão Wi-Fi foi estabelecida corretamente e qual é o IP atribuído.

> Após isso, o servidor web estará ativo e você poderá acessar a câmera pelo navegador usando:

```
http://<IP_DO_ESP32>
```

---

## 💡 Créditos

* Biblioteca ESP32-CAM: [Yoursunny](https://github.com/Yoursunny/esp32cam)
* Placa utilizada: **ESP32-CAM Ai-Thinker**
* Exemplo adaptado para conexão Wi-Fi e servidor HTTP por: **@Isac-Eugenio**

---

## 🚀 Uso rápido

1. Modifique o SSID e senha da sua rede Wi-Fi no código.
2. Compile e envie para o ESP32-CAM Ai-Thinker.
3. Abra o **Monitor Serial** para verificar o IP atribuído.
4. Acesse pelo navegador usando:

```
http://<IP_DO_ESP32>
```

---

## 🎨 Observações de design

* Resoluções menores no MJPEG oferecem mais fluidez e menos consumo de memória.
* Utilize o botão *Stop* do navegador para encerrar streams e liberar a conexão TCP.
* Para projetos de controle de acesso, combine este webserver com sensores e sistemas de autenticação externos.

