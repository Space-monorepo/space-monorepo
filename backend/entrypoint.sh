#!/bin/bash
if [ "$RESET_DB" = "True" ]; then
    python scripts/reset_db.py
fi

python -c "import app.core.init_db"

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload