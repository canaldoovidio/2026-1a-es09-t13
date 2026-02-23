#!/bin/bash

# Script para criar o repositório do Lab de Business Drivers (Semana 03)
# Alvo: https://github.com/canaldoovidio/asis-bd-lab

REPO_DIR="asis-bd-lab"
REMOTE_URL="https://github.com/canaldoovidio/asis-bd-lab.git"

if [ ! -d "$REPO_DIR" ]; then
    echo "Erro: Direitório $REPO_DIR não encontrado."
    exit 1
fi

echo "Iniciando preparação do repositório em $REPO_DIR..."

cd $REPO_DIR

# Inicializa git se não existir
if [ ! -d ".git" ]; then
    git init
    echo "Git inicializado em $REPO_DIR."
fi

# Adiciona arquivos
git add .

# Primeiro commit
git commit -m "feat: Initial commit for ASIS TaxTech Lab (ES09 Week 3)"

# Adiciona o remote
git remote add origin $REMOTE_URL 2>/dev/null || git remote set-url origin $REMOTE_URL

echo "--------------------------------------------------------"
echo "Repositório local preparado!"
echo "Para finalizar a criação no GitHub, execute os comandos abaixo:"
echo ""
echo "cd $REPO_DIR"
echo "git branch -M main"
echo "git push -u origin main"
echo "--------------------------------------------------------"
echo "Nota: Certifique-se de que o repositório 'asis-bd-lab' já foi criado em github.com/canaldoovidio"
