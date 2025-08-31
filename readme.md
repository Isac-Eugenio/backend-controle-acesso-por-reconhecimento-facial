
# Backend Projeto Controle de Acesso por Reconhecimento Facial

## 📌 Introdução

O Backend do Projeto Controle de Acesso por Reconhecimento Facial é a base de um sistema inteligente de autenticação que utiliza visão computacional e biometria facial para controlar e autorizar o acesso de usuários em ambientes físicos ou digitais. Desenvolvido em Python, este backend é estruturado com foco em modularidade, desempenho assíncrono e segurança.

Ele integra tecnologias como FastAPI, OpenCV, face_recognition e MySQL, permitindo o registro, autenticação e gerenciamento de usuários com base em reconhecimento facial. A API pode ser consumida por painéis web, aplicações móveis ou dispositivos embarcados.

### 🔧 Funcionalidades Principais

* 📸 Cadastro de usuários com base em imagens faciais

* 🧠 Reconhecimento facial por vetores de similaridade

* 🔐 Validação de acesso por ID e credenciais

* 🗂️ CRUD completo para usuários (criar, listar, atualizar, excluir)

* 🧪 Sistema de testes automatizados para endpoints e regras

* ⚙️ Arquitetura desacoplada (controllers, services, models e repositórios)

* 📡 API assíncrona e escalável baseada em FastAPI

* 💾 Persistência com banco de dados relacional (MySQL)

* 🔌 Comunicação direta com sistemas  embarcados como Arduino ou ESP32, permitindo controle físico de portas, travas e sensores

---

## 🚀 Instalação

### ✅ Requisitos

* 🐧 **Sistema operacional:** baseado em **Debian Linux** (recomendado: [DietPi](https://dietpi.com))
* ⚙️ **Arquitetura suportada:** ARM64 ou x64
* 📡 **Hardware obrigatório:** pelo menos um **ESP32** e um **ESP32-CAM**
* 🐳 **Docker e Docker Compose instalados**

  * 📦 [Instalar Docker](https://docs.docker.com/engine/install/ubuntu/)
  * 📦 [Instalar Docker Compose](https://docs.docker.com/compose/install/)

---

### 🛠️ Pré-instalação

Antes de iniciar o backend, você deve configurar o firmware dos dispositivos embarcados:

👉 Repositório do firmware:
**[firmware-controle-de-acesso-por-reconhecimento-facial](https://github.com/Isac-Eugenio/firmware-controle-de-acesso-por-reconhecimento-facial)**

Siga o tutorial do repositório acima para instalar o firmware no **ESP32** e no **ESP32-CAM** usados neste projeto.

---

### 📥 Passo a passo para instalar o backend

#### 1. Clone o repositório:

```bash
git clone https://github.com/Isac-Eugenio/backend_controle_de_acesso.git
```

#### 2. Acesse a pasta do projeto:

```bash
cd backend_controle_de_acesso
```
Você pode reescrever essa parte do README.md assim, deixando claro o passo a passo e a relação entre os arquivos:

---

#### 3. Configure os arquivos:

##### 🛠️ Arquivo de configuração da aplicação (`config.yaml`):

1. Vá até o diretório **`core/config`** e edite o arquivo de configuração:

```bash
cd core/config
sudo nano config.yaml
```

2. Dentro dele, configure:

   * Conexão com o banco de dados (`host`, `porta`, `usuário`, `senha`, `nome`)
   * Nome do projeto, permissões de usuário, e demais variáveis de ambiente.

3. para voltar

   * Aperte ctl+o para salvar as modificações
   * Depois ctl+x para fechar o editor e voltar ao terminal
---

##### 🐳 Arquivo de configuração do Docker (`docker-compose.yml`):

1. Volte para a **raiz do projeto**:

```bash
cd ../..
sudo nano docker-compose.yml
```

2. Modifique as variáveis de ambiente do container MySQL:

* `MYSQL_USER`
* `MYSQL_PASSWORD`
* `MYSQL_DATABASE`

⚠️ **Importante:** Os valores definidos no `docker-compose.yml` devem estar **sincronizados** com os que você configurou no `config.yaml`.
Isso garante que o backend consiga se conectar corretamente ao banco MySQL.

---


Show! 👍 Então podemos incluir a observação do `set -e` junto da explicação do `bash -x`. Assim o usuário sabe tanto como **debugar** (`-x`) quanto como **garantir que o script pare no erro** (`set -e`).

Aqui está uma sugestão revisada para o trecho do **README.md**:

---

#### 4. Execute o script de instalação:

```bash
sudo chmod +x install.sh
source install.sh
```

Esse script realiza a instalação das dependências necessárias para o funcionamento do backend.

⚠️ **Importante:** caso haja erros durante a instalação, verifique os arquivos em `.build` (`build_error.log` e `build.log`), onde estarão registrados os detalhes do processo.

Além disso, existem duas formas de facilitar o diagnóstico:

1. **Exibir cada comando antes da execução (debug):**

   ```bash
   sudo bash -x install.sh
   ```

   ou

   ```bash
   sudo bash -x build.sh
   ```

2. **Garantir que o script seja interrompido ao primeiro erro:**
   Inclua no início do arquivo `install.sh` a linha:

   ```bash
   set -e
   ```

   Dessa forma, o script não continuará rodando em caso de falha em algum comando, evitando erros encadeados.

---


#### 5. Inicie o servidor com o script de inicialização:

```bash
chmod +x start.sh
./start.sh
```

Esse script irá:

* ✅ Verificar se o `uvicorn` está instalado e instalar, se necessário
* 🚀 Iniciar a API FastAPI em `0.0.0.0:5050`

---

### ✅ Acesso à API:

* Localmente: [http://localhost:5050](http://localhost:5050)
* Em rede: `http://<IP_DO_SERVIDOR>:5050`

> 🔒 Certifique-se de que a porta `5050` está liberada no firewall ou roteador se quiser acesso externo.

---
