docker container stop expressvpn
docker container rm expressvpn
docker run \
  --env=CODE="$CODE" \
  --env=SERVER=smart \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_PTRACE \
  --device=/dev/net/tun \
  --detach=true \
  --tty=true \
  --name=expressvpn \
  --publish 1080:1080 \
  --publish 8000:8000 \
  --publish 9797:9797 \
  --env=PROTOCOL=lightwayudp \
  --env=ALLOW_LAN=true \
  --env=LAN_CIDR=192.168.1.0/24 \
  --env=METRICS_PROMETHEUS=on \
  --env=CONTROL_SERVER=on \
  --env=SOCKS=on \
  expressvpn:latest \
  /bin/bash
