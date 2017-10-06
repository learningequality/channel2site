FROM nginx
LABEL maintainer="ivan@learningequality.org"
COPY webroot /usr/share/nginx/html
EXPOSE 80
