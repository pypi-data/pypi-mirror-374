import click
import subprocess

# Colores para mensajes
def info(msg):
    click.secho(msg, fg="cyan")

def success(msg):
    click.secho(msg, fg="green")

def warning(msg):
    click.secho(msg, fg="yellow")

def error(msg):
    click.secho(msg, fg="red", bold=True)

# Ejecutar un script sh y mostrar salida
def run_script(script_path, args=None):
    args = args or []
    try:
        result = subprocess.run(
            ["bash", script_path] + args,
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        error(f"❌ Error ejecutando {script_path}")
        return e.returncode
