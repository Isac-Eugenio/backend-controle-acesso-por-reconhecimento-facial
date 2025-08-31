
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
Ah! Entendi. Você quer **inverter a ordem das instruções** para que primeiro o desenvolvedor edite o `docker-compose.yml` na raiz do projeto e depois vá para o `config.yaml` em `core/config`.

Aqui está a versão revisada e reorganizada do seu trecho do README.md:

---

Perfeito! Podemos adicionar instruções **antes da configuração dos arquivos**, orientando o usuário a editar o `init.sql` e ajustar as flags `<adicione o nome da tabela x>` com os nomes reais do projeto. Aqui está a versão revisada:

---

#### 3. Configure os arquivos:

##### 📝 Passo 0: Ajuste inicial do banco (`init.sql`)

Antes de configurar os arquivos do Docker e da aplicação, você precisa **personalizar o script SQL de inicialização**:

1. Abra o arquivo `init.sql` localizado em **`core/db/init.sql`**:

```bash
cd core/db
sudo nano init.sql
```

2. No arquivo, você verá **placeholders** como `<adicione o nome da tabela de dispositivos>`, `<adicione o nome da tabela de usuarios>` e `<adicione o nome da tabela de historico>`.

3. Substitua cada placeholder pelo **nome real da tabela** que deseja usar no seu projeto. Exemplo:

```sql
<adicione o nome da tabela de dispositivos>   → dispositivos
<adicione o nome da tabela de usuarios>      → usuarios
<adicione o nome da tabela de historico>     → historico
```

4. Salve e feche o editor:

* Aperte `Ctrl+O` para salvar
* Aperte `Ctrl+X` para sair

5. Volte para a raiz do projeto para continuar:

```bash
cd ../../
```

---

##### 🐳 Arquivo de configuração do Docker (`docker-compose.yml`):

1. Abra o arquivo na **raiz do projeto**:

```bash
sudo nano docker-compose.yml
```

2. Modifique as variáveis de ambiente do container MySQL:

* `MYSQL_USER`
* `MYSQL_PASSWORD`
* `MYSQL_DATABASE`

⚠️ **Importante:** Os valores definidos no `docker-compose.yml` devem estar **sincronizados** com os que você configurará no `config.yaml`. Isso garante que o backend consiga se conectar corretamente ao banco MySQL.

3. Para salvar e fechar o editor:

* Aperte `Ctrl+O` para salvar as modificações
* Aperte `Ctrl+X` para fechar o editor e voltar ao terminal

##### 🛠️ Arquivo de configuração da aplicação (`config.yaml`):

1. Vá até o diretório **`core/config`** e edite o arquivo de configuração:

```bash
cd core/config
sudo nano config.yaml
```

2. Configure:

* Conexão com o banco de dados
* Conexão com a webcam
* Outros parâmetros necessários

3. Para salvar e fechar:

* Aperte `Ctrl+O` para salvar as modificações
* Aperte `Ctrl+X` para fechar o editor e voltar ao terminal

4. Depois volte para a raiz para continuar a instalação:

```bash
cd ../..
```

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
