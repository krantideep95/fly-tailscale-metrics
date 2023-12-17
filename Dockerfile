FROM alpine:latest

RUN apk update && apk add ca-certificates openrc iptables iptables-legacy ip6tables nginx tailscale \
      && rm -rf /var/cache/apk/* \
      # https://github.com/tailscale/tailscale/issues/10540
      && rm /sbin/iptables && ln -s /sbin/iptables-legacy /sbin/iptables  \
      && rm /sbin/ip6tables && ln -s /sbin/ip6tables-legacy /sbin/ip6tables

# enable tailscale service
RUN rc-update add tailscale default

# don't really know why these next few lines are needed, but they are.
RUN openrc
RUN mkdir -p /run/openrc
RUN touch /run/openrc/softlevel

# https://github.com/neeravkumar/dockerfiles/blob/master/alpine-openrc/Dockerfile#L6-L9
RUN sed -i 's/#rc_sys=""/rc_sys="lxc"/g' /etc/rc.conf &&    echo 'rc_provide="loopback net"' >> /etc/rc.conf

WORKDIR /app

COPY nginx.conf start.sh ./

ENTRYPOINT [ "/app/start.sh" ]
