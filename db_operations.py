from db import get_connection


def create_project_session(image_path, preset_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ProjectSession (image_path, last_used_preset)
        VALUES (?, ?)
    """, (image_path, preset_name))

    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


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

    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return result_id


def link_palette_to_preset(result_id, preset_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO PaletteResult_Preset (result_id, preset_name)
        VALUES (?, ?)
    """, (result_id, preset_name))

    conn.commit()
    conn.close()


def get_all_project_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM ProjectSession
        ORDER BY session_id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_palette_results_for_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM PaletteResult
        WHERE session_id = ?
        ORDER BY result_id DESC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows
