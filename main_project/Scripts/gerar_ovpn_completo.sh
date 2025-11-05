#!/bin/bash

# Diretórios base
PKI_DIR="/home/dougl/openvpn-ca/pki"
TA_KEY="/etc/openvpn/ta.key"
OUTPUT_DIR="/home/dougl/ovpn-gerados"
REMOTE_HOST="179.189.133.252"
PORTA="1150"
PROTOCOLO="udp"

# Lista de clientes
CLIENTES=("client1" "client2" "client3")

# Cria pasta de saída se não existir
mkdir -p "$OUTPUT_DIR"

# Verifica se ta.key existe e é legível
if [[ ! -r "$TA_KEY" ]]; then
  echo "❌ Erro: não foi possível ler $TA_KEY. Execute com sudo ou ajuste permissões."
  exit 1
fi

# Loop para cada cliente
for CLIENTE in "${CLIENTES[@]}"; do
  CRT="$PKI_DIR/issued/$CLIENTE.crt"
  KEY="$PKI_DIR/private/$CLIENTE.key"
  CA="$PKI_DIR/ca.crt"

  if [[ -f "$CRT" && -f "$KEY" && -f "$CA" ]]; then
    echo "📦 Gerando $CLIENTE.ovpn..."

    cat > "$OUTPUT_DIR/$CLIENTE.ovpn" <<EOF
client
dev tun
proto $PROTOCOLO
remote $REMOTE_HOST $PORTA
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-CBC
auth SHA256
remote-cert-tls server
verb 3

<ca>
$(cat "$CA")
</ca>

<cert>
$(awk '/BEGIN/,/END/' "$CRT")
</cert>

<key>
$(cat "$KEY")
</key>

<tls-auth>
$(cat "$TA_KEY")
</tls-auth>
key-direction 1
EOF

    echo "✔ Arquivo $CLIENTE.ovpn criado com sucesso em $OUTPUT_DIR"
  else
    echo "⚠ Erro: arquivos ausentes para $CLIENTE"
    echo "  CRT: $CRT"
    echo "  KEY: $KEY"
    echo "  CA: $CA"
  fi
done
