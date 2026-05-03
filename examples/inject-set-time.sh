#!/bin/bash
# Inject a SET TIME command — syncs device clock to server time.
# The device will pick it up on its next getrequest.aspx poll (every few seconds).

CMD_QUEUE="${ADMS_CMD_QUEUE:-/tmp/adms-cmd-queue.jsonl}"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "{\"id\":\"set-time-$(date +%s)\",\"cmd\":\"SET TIME:${TIMESTAMP}\"}" >> "$CMD_QUEUE"
echo "Queued: SET TIME $TIMESTAMP"
