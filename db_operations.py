import logging
from db import get_connection


def create_project_session(image_path, preset_name=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ProjectSession (image_path, last_used_preset)
            VALUES (?, ?)
        """, (image_path, preset_name))

        conn.commit()
        session_id = cursor.lastrowid
        return session_id

    except Exception:
        logging.exception("Database error in create_project_session")
        raise

    finally:
        if conn:
            conn.close()


def save_palette_result(
    session_id,
    base_color_hex,
    preset_environment,
    preset_style,
    lineart_hex,
    shadow1_hex,
    shadow2_hex,
    highlight1_hex,
    highlight2_hex,
    accent_hex
):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO PaletteResult (
                session_id,
                base_color_hex,
                preset_environment,
                preset_style,
                lineart_hex,
                shadow1_hex,
                shadow2_hex,
                highlight1_hex,
                highlight2_hex,
                accent_hex
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            base_color_hex,
            preset_environment,
            preset_style,
            lineart_hex,
            shadow1_hex,
            shadow2_hex,
            highlight1_hex,
            highlight2_hex,
            accent_hex
        ))

        conn.commit()
        result_id = cursor.lastrowid
        return result_id

    except Exception:
        logging.exception("Database error in save_palette_result")
        raise

    finally:
        if conn:
            conn.close()


def link_palette_to_preset(result_id, preset_name):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO PaletteResult_Preset (result_id, preset_name)
            VALUES (?, ?)
        """, (result_id, preset_name))

        conn.commit()

    except Exception:
        logging.exception("Database error in link_palette_to_preset")
        raise

    finally:
        if conn:
            conn.close()


def get_all_project_sessions():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM ProjectSession
            ORDER BY session_id DESC
        """)

        rows = cursor.fetchall()
        return rows

    except Exception:
        logging.exception("Database error in get_all_project_sessions")
        raise

    finally:
        if conn:
            conn.close()


def get_palette_results_for_session(session_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM PaletteResult
            WHERE session_id = ?
            ORDER BY result_id DESC
        """, (session_id,))

        rows = cursor.fetchall()
        return rows

    except Exception:
        logging.exception("Database error in get_palette_results_for_session")
        raise

    finally:
        if conn:
            conn.close()
