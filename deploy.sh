#!/bin/bash

set -e


APP_NAME="mechassist"
APP_DIR="/var/www/MechAssist"
USER="root"


echo "=== Updating system ==="

apt update
apt upgrade -y


echo "=== Installing packages ==="

apt install -y \
python3 \
python3-pip \
python3-venv \
nginx \
git \
certbot \
python3-certbot-nginx


echo "=== Creating folders ==="

mkdir -p /var/www


echo "=== Creating virtual environment ==="

cd $APP_DIR


python3 -m venv venv


source venv/bin/activate


echo "=== Installing python packages ==="

pip install --upgrade pip

pip install -r requirements.txt



echo "=== Creating systemd service ==="


cat > /etc/systemd/system/$APP_NAME.service <<EOF

[Unit]

Description=MechAssist Flask Application

After=network.target



[Service]

User=$USER

WorkingDirectory=$APP_DIR

ExecStart=$APP_DIR/venv/bin/gunicorn \
--workers 3 \
--bind 127.0.0.1:8000 \
app:app


Restart=always



[Install]

WantedBy=multi-user.target

EOF



systemctl daemon-reload

systemctl enable $APP_NAME

systemctl restart $APP_NAME



echo "=== Nginx config ==="


cat > /etc/nginx/sites-available/$APP_NAME <<EOF


server {

listen 80;


server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;



location / {

proxy_pass http://127.0.0.1:8000;


proxy_set_header Host \$host;

proxy_set_header X-Real-IP \$remote_addr;

proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;

}


location /static/ {

alias $APP_DIR/static/;

}


}

EOF



ln -sf \
/etc/nginx/sites-available/$APP_NAME \
/etc/nginx/sites-enabled/$APP_NAME



rm -f /etc/nginx/sites-enabled/default


nginx -t


systemctl restart nginx



echo "=== DONE ==="

echo "Now run:"
echo "certbot --nginx -d YOUR_DOMAIN.com -d www.YOUR_DOMAIN.com"
