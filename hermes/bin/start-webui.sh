#!/bin/bash

echo "Starting hermes webui on 127.0.0.1:9120"
exec /home/admin/.local/bin/hermes dashboard --host 127.0.0.1 --port 9120 --tui --no-open --insecure
