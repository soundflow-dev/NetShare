#!/bin/bash
# NetShare — vigia da WAN Wi-Fi: garante que a ligação `netshare-wan` está na
# banda 5 GHz preferida. Se estiver em 2.4 GHz (acontece quando o AP cai e
# volta — o autoconnect agarra-se à 2.4 GHz por ter sinal mais forte, antes da
# 5 GHz ficar disponível), força um reconnect para o NM ir buscar a 5 GHz.
#
# Frequência mínima considerada "boa": 5000 MHz (qualquer 5 GHz serve). Pode
# passar-se outra como arg 1 (ex.: 5260 para canal 52 específico).
#
# Tolerante a falhas de propósito (sem `set -e`) — nunca deve abortar a rede.

export LC_ALL=C
CONN=netshare-wan
MIN_FREQ="${1:-5000}"

# Converte uma frequência (MHz) num nome de banda amigável (2.4 GHz / 5 GHz / 6 GHz).
band_name() {
  local f="${1:-}"
  [ -z "$f" ] && { echo "sem ligação"; return; }
  if   [ "$f" -lt 3000 ]; then echo "2.4 GHz"
  elif [ "$f" -lt 6000 ]; then echo "5 GHz"
  elif [ "$f" -lt 8000 ]; then echo "6 GHz"
  else                          echo "${f} MHz"
  fi
}

# A connection está activa?
state=$(nmcli -g GENERAL.STATE connection show "$CONN" 2>/dev/null | head -1)
[ "$state" = "activated" ] || exit 0

# Qual a interface activa?
iface=$(nmcli -g GENERAL.DEVICES connection show "$CONN" 2>/dev/null | head -1)
[ -n "$iface" ] || exit 0

# Que frequência (MHz) está ligado?
freq=$(iw dev "$iface" link 2>/dev/null | awk '/freq:/ {print $2}' | head -1 | cut -d. -f1)
[ -n "$freq" ] || exit 0

if [ "$freq" -lt "$MIN_FREQ" ]; then
  logger -t netshare-wan-watchdog "WAN em $(band_name "$freq") (${freq} MHz) — a forçar reconnect para preferir 5 GHz"
  nmcli connection down "$CONN" >/dev/null 2>&1
  sleep 2
  nmcli connection up "$CONN" >/dev/null 2>&1
  # Confirmar e logar resultado
  new_freq=$(iw dev "$iface" link 2>/dev/null | awk '/freq:/ {print $2}' | head -1 | cut -d. -f1)
  logger -t netshare-wan-watchdog "após reconnect: $(band_name "$new_freq") (${new_freq:-sem ligação} MHz)"
fi
exit 0
