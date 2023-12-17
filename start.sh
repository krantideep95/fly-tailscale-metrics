#!/usr/bin/env sh

# optional - needed to start this VM as tailscale exit node
echo 'net.ipv4.ip_forward = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' | tee -a /etc/sysctl.conf
sysctl -p /etc/sysctl.conf

# start tailscaled daemon
rc-status -a
rc-service tailscale start

# use fly.io secrets to set TAILSCALE_AUTHKEY https://tailscale.com/kb/1132/flydotio#step-1-generate-an-auth-key-to-authenticate-your-app-on-fly
tailscale up \
    --authkey=${TAILSCALE_AUTHKEY} \
    --hostname=fly-${FLY_REGION}-pushgateway \
    --advertise-exit-node

nginx -c /app/nginx.conf
