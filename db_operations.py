from db import get_connection
from datetime import datetime

def create_project_session(image_path, preset_name=None):
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute(""" INSERT INTO ProjectSession (image_path, created_at, last_used_preset) VALUES (?, ?, ?) """, (image_path, datetime.now(), preset_name))

  conn.commit()
  session_id = cursor.lastrowid
  conn.close()
  return session_id

def save_palette_result(session_id, base_color_hex, preset_environment, preset_style, lineart_hex, shadow1_hex, shadow2_hex, highlight1_hex, highlight2_hex, accent_hex):

   conn = get_connection()
   cursor = conn.curspr()              
                
  cursor.execute(""" INSERT INTO PaletteResult (session_id, base_color_hex, preset_environment, preset_style, lineart_hex, shadow1_hex, shadow2_hex, hightlight1_hex, highlight2_hex, accent_hex, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,(
    session_id, base_color_hex, preset_environment, preset_style, lineart_hex, shadow1_hex, shadow2_hex, highlight1_hex, highlight2_hex, accent_hex, datetime.now()
    ))
                 
  conn.commit()
  conn.close()
