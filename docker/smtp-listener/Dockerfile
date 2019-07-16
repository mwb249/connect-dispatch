FROM python:3.7.3-stretch
MAINTAINER Connect Geospatial Solutions <support@connect-geo.com>

ENV PYTHONPATH $PYTHONPATH:/connect-dispatch
ENV DEBIAN_FRONTEND noninteractive


RUN apt update && \
    apt -y install supervisor postfix sasl2-bin opendkim opendkim-tools

# Add files
ADD ./assets /opt/install.sh

# Run
CMD ["postfix", "start -fg"]
