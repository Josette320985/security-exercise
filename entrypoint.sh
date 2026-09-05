#!/bin/sh
set -e

# Generar nginx.conf a partir de la plantilla (reemplazando variables)
envsubst '$BACKEND_URL' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Inyectar API_SECRET en app.js
sed -i "s/{{API_SECRET}}/$API_SECRET/g" /usr/share/nginx/html/app.js

# Iniciar NGINX
nginx -g 'daemon off;'