from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    conn_str = (
        f"mssql+pyodbc://@{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
        f"&trusted_connection=yes"
    )
    return create_engine(conn_str)


def init_db():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='events' AND xtype='U')
            CREATE TABLE events (
                id            INT IDENTITY PRIMARY KEY,
                tag           NVARCHAR(50),
                title         NVARCHAR(255),
                description   NVARCHAR(500),
                image         NVARCHAR(500),
                tag_color     NVARCHAR(50),
                bg_color      NVARCHAR(50),
                date          DATE,
                start_time    NVARCHAR(20),
                end_time      NVARCHAR(20),
                venue         NVARCHAR(255),
                event_link    NVARCHAR(500),
                text_color    NVARCHAR(50),
                title_color   NVARCHAR(50),
                info          NVARCHAR(1000),
                register_text NVARCHAR(255),
                register_link NVARCHAR(500),
                message_id    NVARCHAR(255) UNIQUE,
                uploaded_at   DATETIME DEFAULT GETDATE()
            )
        """))
        conn.commit()
