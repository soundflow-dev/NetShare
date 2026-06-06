#!/bin/bash
# NetShare — rota de retorno de GESTÃO (mantém SSH/web vivos quando a WAN é default).
#
# Problema: quando a Wi-Fi/WAN vira rota default, as respostas do box para um
# admin noutra subnet saem pela WAN e o SSH morre. Solução simples e ROBUSTA:
# uma rota MAIS ESPECÍFICA para a rede de gestão, via a gateway de gestão, na
# tabela principal. Mais específica que o default => ganha sempre, sem policy
# routing nem tabelas separadas (que se mostraram frágeis no arranque).
#
# Portável: lê interface, IP e gateway de gestão ao vivo do NetworkManager
# (ligação "netshare-lan"). A rede do admin assume-se como o /16 à volta do IP
# de gestão (cobre o caso típico de VLANs 10.10.x.x); pode ser passada como arg.
#
# Sem `set -e` de propósito: cada passo é independente e tolerante a falhas,
# para nunca abortar a meio e deixar o routing num estado partido.

export LC_ALL=C            # saída do nmcli/ip em inglês canónico (qualquer idioma)
CONN=netshare-lan
ADMIN_NET="${1:-}"          # override opcional, ex.: 10.10.0.0/16

for attempt in $(seq 1 30); do
  IFACE=$(nmcli -g GENERAL.DEVICES connection show "$CONN" 2>/dev/null | head -1)
  if [ -n "$IFACE" ]; then
    GW=$(nmcli -g IP4.GATEWAY device show "$IFACE" 2>/dev/null | head -1)
    SRC=$(nmcli -g IP4.ADDRESS device show "$IFACE" 2>/dev/null | head -1 | cut -d/ -f1)
    if [ -n "$GW" ] && [ -n "$SRC" ]; then
      net="$ADMIN_NET"
      [ -z "$net" ] && net="$(echo "$SRC" | cut -d. -f1-2).0.0/16"
      if ip route replace "$net" via "$GW" dev "$IFACE" metric 50 2>/dev/null; then
        logger -t netshare-mgmt-route "rota de gestao OK: $net via $GW dev $IFACE"
        exit 0
      fi
    fi
  fi
  sleep 2
done
logger -t netshare-mgmt-route "AVISO: nao consegui fixar a rota de gestao apos 30 tentativas"
exit 0
