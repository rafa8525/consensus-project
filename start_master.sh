#!/bin/bash
set +e
cd "$HOME/consensus-project" 2>/dev/null || true
set -a; [ -f .env ] && source .env || echo "WARN: .env missing"; set +a
[ -z "$SMS_TO_NUMBER" ] && [ -n "$TWILIO_TO_NUMBER" ] && export SMS_TO_NUMBER="$TWILIO_TO_NUMBER"
[ -z "$WEATHER_API_KEY" ] && [ -n "$OPENWEATHER_API_KEY" ] && export WEATHER_API_KEY="$OPENWEATHER_API_KEY"
exec python3.10 master_control_loop.py
