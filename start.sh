#!/bin/bash
# ---------------------------------------------------------
# Script para verificar a instalação do Uvicorn e iniciar
# um servidor FastAPI na porta 5050.
# ---------------------------------------------------------

# Verifica se o comando 'uvicorn' está disponível no sistema
if ! command -v uvicorn &> /dev/null; then
    # Se não estiver instalado, exibe mensagem e instala
    echo "⚠️ Uvicorn não está instalado. Instalando..."
    sudo apt update && sudo apt install -y uvicorn
else
    # Se já estiver instalado, exibe mensagem de confirmação
    echo "✅ Uvicorn já está instalado."
fi

# Exibe mensagem indicando que o servidor vai iniciar
echo "🚀 Iniciando servidor FastAPI..."

# Inicia o servidor FastAPI usando uvicorn
# - main:app  -> aponta para o arquivo main.py e a instância 'app' do FastAPI
# - --host 0.0.0.0 -> permite acesso externo ao servidor
# - --port 5050 -> define a porta de escuta do servidor
uvicorn main:app --host 0.0.0.0 --port 5050
