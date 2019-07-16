FROM python:3.7.3-stretch
MAINTAINER Connect Geospatial Solutions <support@connect-geo.com>

ENV PYTHONPATH $PYTHONPATH:/connect-dispatch

# Prepare directory
RUN mkdir /connect-disptach
WORKDIR /connect-dispatch

RUN apt update && \
    apt -y --no-install-recommends install \
      incron && \
    apt clean
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
# ADD requirements.txt /connect-dispatch/
# RUN pip install -r requirements.txt

COPY . /connect-dispatch/

RUN echo "root" > /etc/incron.allow
COPY incron-table.txt /etc/incron.d/incron-table

CMD ["/usr/sbin/incrond", "-n"]
