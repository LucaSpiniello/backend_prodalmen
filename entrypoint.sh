#!/bin/sh
# entrypoint.sh

# Export environment variables
export $(grep -v '^#' /codigo_proyecto/.env | xargs)

# Run the Django server with Daphne
daphne -b 0.0.0.0 -p 8000 prodalwebV3.asgi:application
