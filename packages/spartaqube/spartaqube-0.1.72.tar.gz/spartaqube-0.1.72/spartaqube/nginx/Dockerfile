FROM nginx:1.19.0-alpine

COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# RUN mkdir ./app
# RUN mkdir ./app/static
# COPY ./static ./app/static

# COPY ./spartaquantssl+4-key.pem /etc/nginx/certs/spartaquantssl+4-key.pem
# COPY ./spartaquantssl+4.pem /etc/nginx/certs/spartaquantssl+4.pem

# COPY ./nginx-selfsigned.crt /etc/nginx/certs/nginx-selfsigned.crt
# COPY ./nginx-selfsigned.key /etc/nginx/certs/nginx-selfsigned.key
# COPY ./dhparam.pem /etc/nginx/certs/dhparam.pem

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/errorlog

# CMD tail -f /dev/null
CMD ["nginx", "-g", "daemon off;"]