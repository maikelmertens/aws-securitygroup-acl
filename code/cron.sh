#!/usr/bin/env sh

if [ "${BLACKLIST}" = "true" ]; then
  EXTRA_OPTS="-b ${EXTRA_OPTS}"
fi

CRON_CMD="/code/main.sh -i ${SECURITY_GROUP_IDS} -f ${OUTPUT_FORMAT} -od /acl ${EXTRA_OPTS}"
echo "${CRON} ${CRON_CMD} > /proc/1/fd/1" > /etc/crontabs/root

# first initialize immediately without cron
${CRON_CMD}

crond -f
