import os

def run(cmd):
    print(f"Executando: {cmd}")
    os.system(cmd)

# Atualizar e instalar pacotes
run("sudo apt update")
run("sudo apt install easy-rsa openvpn -y")

# Preparar diretório EasyRSA
run("mkdir -p ~/openvpn-ca")
run("cp -r /usr/share/easy-rsa/* ~/openvpn-ca/")
run("cd ~/openvpn-ca")

# Inicializar PKI e construir CA
run("cd ~/openvpn-ca && ./easyrsa init-pki")
run("cd ~/openvpn-ca && ./easyrsa build-ca nopass")

# Solicitar variáveis ao usuário
print("\nPor favor, insira os dados para configurar os certificados:")
country = input("País (EASYRSA_REQ_COUNTRY): ")
province = input("Estado/Província (EASYRSA_REQ_PROVINCE): ")
city = input("Cidade (EASYRSA_REQ_CITY): ")
org = input("Organização (EASYRSA_REQ_ORG): ")
email = input("Email (EASYRSA_REQ_EMAIL): ")
ou = input("Unidade Organizacional (EASYRSA_REQ_OU): ")
cn = input("Nome Comum (EASYRSA_REQ_CN): ")

# Escrever variáveis no arquivo vars
vars_path = os.path.expanduser("~/openvpn-ca/vars")
with open(vars_path, "a") as f:
    f.write(f'\nset_var EASYRSA_REQ_COUNTRY    "{country}"\n')
    f.write(f'set_var EASYRSA_REQ_PROVINCE   "{province}"\n')
    f.write(f'set_var EASYRSA_REQ_CITY       "{city}"\n')
    f.write(f'set_var EASYRSA_REQ_ORG        "{org}"\n')
    f.write(f'set_var EASYRSA_REQ_EMAIL      "{email}"\n')
    f.write(f'set_var EASYRSA_REQ_OU         "{ou}"\n')
    f.write(f'set_var EASYRSA_REQ_CN         "{cn}"\n')


# Reexecutar inicialização e CA
run("cd ~/openvpn-ca && ./easyrsa init-pki")
run("cd ~/openvpn-ca && ./easyrsa build-ca nopass")

# Gerar chave do servidor
run("cd ~/openvpn-ca && ./easyrsa gen-req server nopass")
run("cd ~/openvpn-ca && ./easyrsa sign-req server server")
run("cd ~/openvpn-ca && ./easyrsa gen-dh")

# Gerar chave ta.key
run("mkdir -p ~/openvpn-ca/keys")
run("cd ~/openvpn-ca && openvpn --genkey secret keys/ta.key")

# Perguntar quantos certificados de cliente gerar
try:
    num_clients = int(input("Quantos certificados de cliente deseja gerar? "))
    for i in range(1, num_clients + 1):
        client_name = f"client{i}"
        run(f"cd ~/openvpn-ca && ./easyrsa gen-req {client_name} nopass")
        run(f"cd ~/openvpn-ca && ./easyrsa sign-req client {client_name}")
except ValueError:
    print("Entrada inválida. Por favor, insira um número inteiro.")

# Configurar ficheiro de servidor
run("gunzip -c /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz > /etc/openvpn/server.conf")

# Copiar certificados e chaves
run("sudo cp ~/openvpn-ca/pki/ca.crt /etc/openvpn/")
run("sudo cp ~/openvpn-ca/pki/issued/server.crt /etc/openvpn/")
run("sudo cp ~/openvpn-ca/pki/private/server.key /etc/openvpn/")
run("sudo cp ~/openvpn-ca/pki/dh.pem /etc/openvpn/")
run("sudo cp ~/openvpn-ca/keys/ta.key /etc/openvpn/")

# Iniciar e habilitar OpenVPN
run("sudo systemctl start openvpn@server")
run("sudo systemctl enable openvpn@server")


"""

sudo apt update
sudo apt install easy-rsa openvpn -y

mkdir ~/openvpn-ca
cp -r /usr/share/easy-rsa/* ~/openvpn-ca/
cd ~/openvpn-ca


./easyrsa init-pki
./easyrsa build-ca

nano ~/openvpn-ca/vars

set_var EASYRSA_REQ_COUNTRY    "BR"
set_var EASYRSA_REQ_PROVINCE   "RS"
set_var EASYRSA_REQ_CITY       "Rio Grande"
set_var EASYRSA_REQ_ORG        "MinhaEmpresaVPN"
set_var EASYRSA_REQ_EMAIL      "email@exemplo.com"
set_var EASYRSA_REQ_OU         "VPN"
set_var EASYRSA_REQ_CN         "server"

./easyrsa init-pki
./easyrsa build-ca

# Server Key

./easyrsa gen-req server nopass
./easyrsa sign-req server server
./easyrsa gen-dh

# Gerar as keys, senao me engano este diretorio fica internamente no EasyRSA

mkdir -p keys
openvpn --genkey secret keys/ta.key

# Certificados aos CLientes, automatizar pegunta ao Usuario de quantos certificados ele quer

./easyrsa gen-req client1 nopass
./easyrsa sign-req client client1

# COnfigurando os ficheiros para funcionamento do OpenVPN

gunzip -c /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz > /etc/openvpn/server.conf


# Copiar tudo ao diretório do OpenVPN

sudo cp ~/openvpn-ca/pki/ca.crt /etc/openvpn/
sudo cp ~/openvpn-ca/pki/issued/server.crt /etc/openvpn/
sudo cp ~/openvpn-ca/pki/private/server.key /etc/openvpn/
sudo cp ~/openvpn-ca/pki/dh.pem /etc/openvpn/
sudo cp ~/openvpn-ca/keys/ta.key /etc/openvpn/

# Iniciar o OpenVPN

sudo systemctl start openvpn@server
sudo systemctl enable openvpn@server

