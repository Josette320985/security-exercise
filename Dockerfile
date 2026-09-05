FROM nginx:alpine

RUN apk add --no-cache gettext

COPY nginx.conf /etc/nginx/nginx.conf.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY html/ /usr/share/nginx/html

EXPOSE 80

ENTRYPOINT ["sh", "/entrypoint.sh"]
