#!/usr/bin/env bash

set -e

if [ "${EUID}" -ne 0 ]; then
  echo "このスクリプトは root 権限で実行してください"
  exit 1
fi

if [ $# -lt 2 ]; then
    echo "$0 Usage"
    echo "    $0 arg1 arg2 arg3 arg4"
    echo "        - arg1 : ユーザ名"
    echo "        - arg2 : チーム番号(2桁)"
    echo "        - arg3 : net28 割り当て最小値(デフォルト : 5)"
    echo "        - arg4 : net28 割り当て最大値(デフォルト : 10)"
    exit 1
fi

profileName="Wired connection 2"
teamID=$(printf "%02d" "$((10#$2))")
today=$(date +%Y%m%d)
TARGETUSER=$1
minAddr=5

if [ -n "$3" ]; then
    minAddr=$3
fi

maxAddr=10

if [ -n "$4" ]; then
    maxAddr=$4
fi

if ! nmcli connection show "${profileName}" &> /dev/null; then
    # 新しい接続プロファイルを作成
    nmcli connection add type ethernet              \
        con-name "${profileName}"                   \
        ifname eth1
fi

# 接続プロファイルを編集
nmcli connection modify "${profileName}"            \
    ipv4.method manual                              \
    ipv4.addresses "192.168.2${teamID}.1/28"        \
    ipv4.gateway "192.168.2${teamID}.1"             \
    ipv4.dns "192.168.2${teamID}.1"                 \
    ipv4.route-metric 200                           \
    ipv4.dns-priority 200                           \
    ipv6.method ignore

nmcli connection reload
nmcli connection down "${profileName}"
nmcli connection up "${profileName}"

cp "/etc/dnsmasq.conf" "/home/${TARGETUSER}/dnsmasq.conf.${today}"

if [ ! -f "/home/${TARGETUSER}/dnsmasq.conf.backup.${today}" ]; then
    cp "/home/${TARGETUSER}/dnsmasq.conf.${today}" "/home/${TARGETUSER}/dnsmasq.conf.backup.${today}"
fi


# net24 → net28
# dnsmasq設定ファイルの編集

sed -i "s/192.168.10/192.168.20/g" "/home/${TARGETUSER}/dnsmasq.conf.${today}"
sed -i "s/192.168.11/192.168.21/g" "/home/${TARGETUSER}/dnsmasq.conf.${today}"

# arpa変更
sed -i "s/^server=\/10/server=\/20/" "/home/${TARGETUSER}/dnsmasq.conf.${today}"
sed -i "s/^server=\/11/server=\/21/" "/home/${TARGETUSER}/dnsmasq.conf.${today}"

sed -i "s/^server=\/20\./server=\/10\./" "/home/${TARGETUSER}/dnsmasq.conf.${today}"

sed -i \
    "s/^dhcp-range=.*/dhcp-range=192.168.2${teamID}.${minAddr},192.168.2${teamID}.${maxAddr},255.255.255.240,24h/" \
    "/home/${TARGETUSER}/dnsmasq.conf.${today}"
# dnsmasq上書き
cp "/home/${TARGETUSER}/dnsmasq.conf.${today}" "/etc/dnsmasq.conf"

systemctl restart dnsmasq.service
apt update && apt upgrade -y
# apt install -y traceroute tcpdump dnsutils 