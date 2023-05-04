FROM public.ecr.aws/docker/library/python:3.11.3-bullseye

RUN apt-get update && apt-get -yq install supervisor tzdata less nginx \
  && rm -rf /var/lib/apt/lists/*

# TimeZone
RUN echo "Asia/Tokyo" > /etc/timezone \
  && rm /etc/localtime \
  && ln -s /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
  && dpkg-reconfigure -f noninteractive tzdata

COPY ./module/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt


COPY ./nginx/default /etc/nginx/sites-available/default
RUN ln -s -f /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
COPY ./supervisor/supervisor.conf /etc/supervisor/conf.d/supervisor.conf
COPY ./app /usr/local/app

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
