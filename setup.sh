#!/bin/bash

function check_install_pkg {
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1|grep "install ok installed")
    echo Checking for $1: $PKG_OK
    if [ "" == "$PKG_OK" ]; then
        echo "$1 not installed. Setting up $1."
        apt-get --yes install $1
    else
        echo "$1 already installed."
    fi
}

echo "Installing pip, nginx, and uwsgi"
check_install_pkg python-pip
check_install_pkg nginx
check_install_pkg uwsgi-core

echo "Installing neo4j"
if [ ! -e "/etc/apt/sources.list.d/neo4j.list" ]; then
    wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
    echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
    apt-get update
fi
check_install_pkg neo4j

echo "Create Whili user"
adduser --no-create-home --disabled-login www-whili

echo "Setting up services."
mkdir -p /var/run/neo4j
NEO4J=$(which neo4j)
cat < EOF > /etc/systemd/system/neo4j.service
[Unit]
Description=Neo4j Management Service
After=syslog.target

[Service]
Type=forking
User=neo4j
ExecStart=/usr/bin/neo4j start
ExecStop=/usr/bin/neo4j stop
RemainAfterExit=no
Restart=on-failure
PIDFile=/opt/neo4j-community-3.2.0/run/neo4j.pid
LimitNOFILE=60000
TimeoutSec=600

[Install]
WantedBy=multi-user.target
EOF

cat < EOF > /etc/systemd/system/whitelightning.uwsgi.service
[Unit]
Description=uWSGI for WhiteLightning
After=neo4j.service

[Service]
Environment="PATH=/var/www/WhiteLightningSE/whitelightning/bin"
WorkingDirectory=/var/www/WhiteLightningSE/
User=www-whili
Group=www-data
ExecStart=/usr/local/bin/uwsgi --ini conf/whitelightning.conf
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF

cat < EOF > /etc/systemd/system/nginx.service
[Unit]
Description=A high performance web server and a reverse proxy server
After=whitelightning.uwsgi.service

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t -q -g 'daemon on; master_process on;'
ExecStart=/usr/sbin/nginx -g 'daemon on; master_process on;'
ExecReload=/usr/sbin/nginx -g 'daemon on; master_process on;' -s reload
ExecStop=-/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid
TimeoutStopSec=5
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/www/WhiteLightningSE
cp -R app/ /var/www/WhiteLightningSE/.
cp -R conf/ /var/www/WhiteLightningSE/.
cp _config.yml /var/www/WhiteLightningSE/.
cp requirements.txt /var/www/WhiteLightningSE/.
