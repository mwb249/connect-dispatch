FROM python:3.7.3-stretch
MAINTAINER Connect Geospatial Solutions <support@connect-geo.com>

ENV PYTHONPATH $PYTHONPATH:/connect-dispatch

# Prepare directory
RUN mkdir /connect-disptach
WORKDIR /connect-dispatch

RUN apt update && \
    apt -y --no-install-recommends install \
      cron && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
ADD requirements.txt /connect-dispatch/
RUN apt update && pip install -r requirements.txt

COPY . /connect-dispatch/

COPY cron-table.txt /etc/cron.d/cron-table

# Give execution rights on the cron-worker job
RUN chmod 0644 /etc/cron.d/cron-table

# Apply cron-worker job
RUN crontab /etc/cron.d/cron-table

CMD ["cron", "-f"]
