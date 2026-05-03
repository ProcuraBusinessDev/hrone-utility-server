#!/bin/bash
# Inject a CHECK command — device replies with its current status.

CMD_QUEUE="${ADMS_CMD_QUEUE:-/tmp/adms-cmd-queue.jsonl}"

echo "{\"id\":\"check-$(date +%s)\",\"cmd\":\"CHECK\"}" >> "$CMD_QUEUE"
echo "Queued: CHECK"
