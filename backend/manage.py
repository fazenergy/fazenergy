#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# Debugpy opcional/controlado por env e apenas no runserver
ENABLE_DEBUGPY = os.environ.get("ENABLE_DEBUGPY") == "1"
DEBUGPY_PORT = int(os.environ.get("DEBUGPY_PORT", "5678"))

# Protege para só ativar o debug uma vez (evita erro de porta)
if ENABLE_DEBUGPY and os.environ.get("RUN_MAIN") != "true" and ("runserver" in sys.argv or os.environ.get("ALWAYS_DEBUGPY") == "1"):
    try:
        import debugpy
        debugpy.listen(("0.0.0.0", DEBUGPY_PORT))
        print(f"🔍 Aguardando debugger conectar na porta {DEBUGPY_PORT}...")
        # debugpy.wait_for_client()  # opcional se quiser pausar
    except Exception as e:
        print(f"⚠️ Debugpy indisponível na porta {DEBUGPY_PORT}: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
