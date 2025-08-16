#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
try:
    import debugpy  # type: ignore
    # Protege para só ativar o debug uma vez (evita erro de porta)
    if os.environ.get("RUN_MAIN") != "true":
        debugpy.listen(("0.0.0.0", 5678))
        print("🔍 Aguardando debugger conectar na porta 5678...")
        # debugpy.wait_for_client()  # opcional se quiser pausar
except Exception:
    # Se não existir debugpy no ambiente, ignora silenciosamente
    debugpy = None

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
