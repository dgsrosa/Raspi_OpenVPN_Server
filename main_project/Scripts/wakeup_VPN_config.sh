#!/bin/bash

# Habilita encaminhamento IP
sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Aplica regra de NAT para VPN
iptables -t nat -C POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE 2>/dev/null || \
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
sudo ip6tables -A INPUT -p udp --dport 1150 -j ACCEPT
