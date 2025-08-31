#!/bin/bash
set +m  # Desativa mensagens de job control tipo '[1]+ Done'

# ---------------------------
# Configuração de diretórios e logs
# ---------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # Diretório do script
LOGFILE="$SCRIPT_DIR/build.log"        # Log geral de execução
ERRORLOG="$SCRIPT_DIR/build_error.log" # Log de erros

# Limpa logs antigos
> "$LOGFILE"
> "$ERRORLOG"

# ---------------------------
# Cores para saída de terminal
# ---------------------------
GREEN="\033[0;32m"  # Verde para sucesso
RED="\033[0;31m"    # Vermelho para erros
YELLOW="\033[1;33m" # Amarelo para avisos/log
NC="\033[0m"         # Sem cor (reset)

# ---------------------------
# Funções de log
# ---------------------------
log() {
    # Escreve mensagem de log amarela e salva no logfile
    echo -e "${YELLOW}[LOG]${NC} $1" | tee -a "$LOGFILE"
}

error() {
    # Escreve mensagem de erro vermelha e salva no errorlog
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$ERRORLOG" >&2
}

# ---------------------------
# Spinner visual para indicar execução em background
# ---------------------------
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    echo -n " "
    while kill -0 $pid 2>/dev/null; do  # Enquanto o processo existir
        local temp=${spinstr#?}
        printf "\b%c" "$spinstr"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
    done
    printf "\b"
}

# ---------------------------
# Função para executar comando com spinner e tratamento de erros
# ---------------------------
run_spinner() {
    log "$1"  # Mostra log do comando
    bash -c "$1" >>"$LOGFILE" 2>>"$ERRORLOG" &  # Executa comando em background, redirecionando logs
    pid=$!
    spinner $pid
    wait $pid
    status=$?
    if [ $status -ne 0 ]; then
        error "Falha ao executar: $1"
        exit 1
    fi
}

# ---------------------------
# Atualização e instalação de dependências do sistema
# ---------------------------
log "Iniciando instalação de dependências do sistema..."
run_spinner "sudo apt update"
run_spinner "sudo apt upgrade -y"

run_spinner "sudo apt install -y python3-venv build-essential cmake python3-dev python3-pip \
libopenblas-dev libboost-all-dev libx11-dev libjpeg-dev libpng-dev libgl1-mesa-glx libglib2.0-0 libgtk-3-dev"
# Instala ferramentas de compilação, bibliotecas de imagens, OpenBLAS, Boost, CMake, Python Dev, etc.

# ---------------------------
# Criação e ativação do ambiente virtual Python
# ---------------------------
log "Criando ambiente virtual..."
run_spinner "python3 -m venv .venv"  # Cria venv no projeto

log "Atualizando pip dentro do ambiente virtual..."
run_spinner "source .venv/bin/activate && pip install --upgrade pip"

# ---------------------------
# Instalação das dependências Python do projeto
# ---------------------------
log "⚙️  Instalando dependências Python (compilação do dlib pode demorar alguns minutos)..."
bash -c "source .venv/bin/activate && pip install -r requirements.txt" >>"$LOGFILE" 2>>"$ERRORLOG" &
pid=$!
spinner $pid
wait $pid
status=$?
if [ $status -ne 0 ]; then
    error "Falha ao instalar requirements.txt (provavelmente na compilação do dlib)"
    exit 1
fi

# ---------------------------
# Inicialização do banco de dados via Docker Compose
# ---------------------------
log "🐳 Subindo banco de dados do projeto com Docker Compose..."
run_spinner "docker compose up -d"

# ---------------------------
# Conclusão
# ---------------------------
log "Todos os serviços foram iniciados com sucesso!"
echo -e "${GREEN}[✓] Build finalizado e banco de dados iniciado via Docker Compose!${NC}"
