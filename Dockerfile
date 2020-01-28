FROM python:3.8-alpine

ENV CRON "*/5 * * * *"
ENV SECURITY_GROUP_ID ""
ENV OUTPUT_FORMAT plain
ENV OUTPUT_FILE whitelist.acl
ENV BLACKLIST false

COPY ./code/ /code/
RUN chmod +x /code/*.sh && \
    mkdir -p /acl && \
    pip install --upgrade pip && \
    pip install --requirement /code/requirements.txt --upgrade

WORKDIR /acl
VOLUME /acl

CMD [ "/code/cron.sh" ]
