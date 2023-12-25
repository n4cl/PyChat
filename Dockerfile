FROM public.ecr.aws/docker/library/python:3.11.6-bullseye

RUN apt-get update && apt-get -yq install supervisor tzdata less nginx \
  ca-certificates curl gnupg \
  && rm -rf /var/lib/apt/lists/*

# Node.js
RUN mkdir -p /etc/apt/keyrings && \
  curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
  NODE_MAJOR=20 && \
  echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get -yq install nodejs \
  && rm -rf /var/lib/apt/lists/*

# TimeZone
RUN echo "Asia/Tokyo" > /etc/timezone \
  && rm /etc/localtime \
  && ln -s /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
  && dpkg-reconfigure -f noninteractive tzdata

# Backend build
COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt


COPY ./nginx/default /etc/nginx/sites-available/default
RUN ln -s -f /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
COPY ./supervisor/supervisor.conf /etc/supervisor/conf.d/supervisor.conf
COPY ./ /usr/local/app

# Frontend のリンク
RUN ln -s /usr/local/app/frontend/app /usr/share/nginx/html

ARG ENV
RUN if [ "$ENV" = "development" ] ; then \
    pip install -r /usr/local/app/backend/requirements-dev.txt && \
    npm install --prefix /usr/local/app/frontend \
; else \
    npm install --prefix /usr/local/app/frontend --production \
; fi

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
