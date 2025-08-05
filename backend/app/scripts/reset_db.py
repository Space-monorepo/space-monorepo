from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import engine

with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.commit()

print("Banco resetado com sucesso!")