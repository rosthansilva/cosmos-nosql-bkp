#!/bin/bash

# Instalar azcopy
echo "Atualizando pacotes e instalando dependências..."
apt-get update
apt-get install -y wget

echo "Baixando e instalando o pacote Microsoft..."
wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
apt-get update
apt-get install -y azcopy
rm -f packages-microsoft-prod.deb

# Verificar se as variáveis de ambiente necessárias estão definidas
if [[ -z "$AZURE_STORAGE_ACCOUNT" || -z "$AZURE_CONTAINER_NAME" || -z "$AZCOPY_TENANT_ID" ]]; then
    echo "Erro: Certifique-se de que as variáveis AZURE_STORAGE_ACCOUNT, AZURE_CONTAINER_NAME e AZCOPY_TENANT_ID estão definidas no ambiente."
    exit 1
fi

# Copiar arquivos para o Azure Blob Storage
echo "Sincronizando arquivos com o Azure Blob Storage..."
azcopy sync --compare-hash=md5 \
    --delete-destination=true \
    --include-pattern="$1" \
    "." "https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${AZURE_CONTAINER_NAME}/"

echo "Sincronização concluída."