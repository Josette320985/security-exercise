import os
import time
import secrets
import re

# Ruta al archivo app.js dentro del contenedor backend (volumen compartido)
JS_PATH = "/shared-html/app.js"

def update_frontend_secret(new_secret):
    try:
        with open(JS_PATH, "r") as f:
            content = f.read()
        # Buscar línea: const API_KEY = "...";
        pattern = r'(const\s+API_KEY\s*=\s*")[^"]*(";)'
        new_content = re.sub(pattern, f'\\g<1>{new_secret}\\g<2>', content)
        with open(JS_PATH, "w") as f:
            f.write(new_content)
        print(f"[rotate] Updated frontend API_KEY to {new_secret}")
    except Exception as e:
        print(f"[rotate] Error updating frontend: {e}")

def rotate_secret():
    new_secret = secrets.token_urlsafe(32)
    os.environ["API_SECRET"] = new_secret
    update_frontend_secret(new_secret)
    # Escribe el nuevo secreto en un archivo
    with open("/app/.secret", "w") as f:
        f.write(new_secret)
    print(f"[rotate] New API_SECRET: {new_secret}")

if __name__ == "__main__":
    print("[rotate] Starting secret rotation every 2 minutes...")
    while True:
        rotate_secret()
        time.sleep(120)   # 2 minutos