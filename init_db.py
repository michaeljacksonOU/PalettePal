import logging
from db import get_connection


def initialize_database():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProjectSession (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_used_preset TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PaletteResult (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            base_color_hex TEXT NOT NULL,
            preset_environment TEXT NOT NULL,
            preset_style TEXT,
            lineart_hex TEXT NOT NULL,
            shadow1_hex TEXT NOT NULL,
            shadow2_hex TEXT NOT NULL,
            highlight1_hex TEXT NOT NULL,
            highlight2_hex TEXT NOT NULL,
            accent_hex TEXT NOT NULL,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES ProjectSession(session_id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PresetDefinition (
            preset_name TEXT PRIMARY KEY,
            light_temp TEXT NOT NULL,
            shadow_temp TEXT NOT NULL,
            temp_strength REAL NOT NULL,
            hsv_delta_values TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PaletteResult_Preset (
            result_id INTEGER NOT NULL,
            preset_name TEXT NOT NULL,
            PRIMARY KEY (result_id, preset_name),
            FOREIGN KEY (result_id) REFERENCES PaletteResult(result_id) ON DELETE CASCADE,
            FOREIGN KEY (preset_name) REFERENCES PresetDefinition(preset_name) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CalibrationSwatch (
            hex TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            category TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserAccount (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Challenge (
            challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_at DATETIME NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChallengeSubmission (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            palette_result_id INTEGER NOT NULL,
            image_path TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            sync_status TEXT DEFAULT 'pending',
            FOREIGN KEY (challenge_id) REFERENCES Challenge(challenge_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES UserAccount(user_id) ON DELETE CASCADE,
            FOREIGN KEY (palette_result_id) REFERENCES PaletteResult(result_id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        print("Database initialized successfully.")

    except Exception:
        logging.exception("Database initialization failed")
        raise

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    initialize_database()
