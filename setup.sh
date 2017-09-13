#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo " [!] This script must be run as root" 1>&2
   exit 1
fi

function check_install_pkg {
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1|grep "install ok installed")
    echo "[ ] Checking for $1: $PKG_OK"
    if [ "" == "$PKG_OK" ]; then
        echo "[-] $1 not installed. Setting up $1."
        apt-get --yes -q=2 install $1
    else
        echo "[+] $1 already installed."
    fi
}

echo "[ ] Installing pip, nginx, and uwsgi"
check_install_pkg python-pip
check_install_pkg nginx

echo "[ ] Installing neo4j"
if [ ! -e "/etc/apt/sources.list.d/neo4j.list" ]; then
    wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
    echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
    apt-get update
fi
check_install_pkg neo4j

echo "[ ] Creating www-whili user"
adduser www-whili --disabled-login --system --disabled-password --ingroup www-data --home /var/www/WhiteLightningSE --shell /bin/false

echo "[ ] Setting up services."
mkdir -p /var/run/neo4j
touch /var/log/uwsgi.log
chown www-whili:www-data /var/log/uwsgi.log
chmod 660 /var/log/uwsgi.log
cat << EOF > /etc/systemd/system/whitelightning.uwsgi.service
[Unit]
Description=uWSGI for WhiteLightning
After=neo4j.service

[Service]
WorkingDirectory=/var/www/WhiteLightningSE/app
User=www-whili
Group=www-data
ExecStart=/usr/local/bin/uwsgi --ini ../conf/uwsgi.conf
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOF

echo "[?] Enter the FQDN of your server (or IP): "
read FQDN

cp /etc/nginx/nginx.conf{,.bak}
cat << EOF > /etc/nginx/nginx.conf
worker_processes auto;
user www-whili www-data;

events {
    worker_connections 4096;
}

http{
server {
    listen 80;
    server_name $FQDN;
    access_log /var/log/nginx_access.log;
    error_log /var/log/nginx_error.log;
    error_page   404  /404.html;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/WhiteLightningSE/whitelightning.sock;
        uwsgi_param   UWSGI_CHDIR     /var/www/WhiteLightning/app;
        uwsgi_param   UWSGI_MODULE    routes;
        uwsgi_param   UWSGI_CALLABLE  app;
    }
}
}
EOF

mkdir -p /var/www/WhiteLightningSE
cp -R app/ /var/www/WhiteLightningSE/.
cp -R conf/ /var/www/WhiteLightningSE/.
cp _config.yml /var/www/WhiteLightningSE/.
cp requirements.txt /var/www/WhiteLightningSE/.

cat << EOF > /var/www/WhiteLightningSE/conf/uwsgi.conf
[uwsgi]
module = routes
callable = app
master = true
processes = 5
socket = /var/www/WhiteLightningSE/whitelightning.sock
chmod-socket = 660
vacuum = true
die-on-term = true
logger = file:/var/log/uwsgi.log
EOF

chown -R www-whili:www-data /var/www/WhiteLightningSE

cd /var/www/WhiteLightningSE/
pip install -r requirements.txt

systemctl enable neo4j
systemctl start neo4j
systemctl enable whitelightning.uwsgi
systemctl start whitelightning.uwsgi
systemctl reload nginx

echo "[ ] Setup complete. You can now access the site at http://$FQDN/"
echo "[!] Recommend setting up SSL (e.g. with LetsEncrypt)"
echo "sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot

certbot --nginx

systemctl restart nginx

#Auto-renew
crontab -e
27 3 * * * /usr/bin/certbot renew --quiet --renew-hook \"/usr/sbin/systemctl reload-or-restart nginx\""
