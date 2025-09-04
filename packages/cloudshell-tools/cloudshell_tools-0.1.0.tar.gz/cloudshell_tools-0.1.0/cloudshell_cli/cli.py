import os
from . import utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

@click.group()
def cli():
    """CLI para automatizar tareas en AWS CloudShell."""
    pass

@click.command()
def run_ecr():
    utils.info("🚀 Este comando loguea en ECR y corre una imagen Docker.")
    script = os.path.join(SCRIPTS_DIR, "correr-docker-ecr.sh")
    utils.run_script(script)

@click.command()
def ecs_fargate():
    utils.info("📦 Este comando ejecuta un template.yaml de CloudFormation para lanzar ECS Fargate.")
    script = os.path.join(SCRIPTS_DIR, "deploy-ecs.sh")
    utils.run_script(script)

@click.command()
def buscar_buckets():
    utils.info("🔍 Este comando busca coincidencias de archivos en S3.")
    script = os.path.join(SCRIPTS_DIR, "buscar-archivo-s3.sh")
    utils.run_script(script)

@click.command()
def crear_y_subir_imagen_ecr():
    utils.info("🐳 Este comando contruye y despliega una imagen de docker en ECR.")
    script = os.path.join(SCRIPTS_DIR, "crear-y-subir-imagen-ecr.sh")
    utils.run_script(script)

cli.add_command(run_ecr)
cli.add_command(ecs_fargate)
cli.add_command(buscar_buckets)
cli.add_command(crear_y_subir_imagen_ecr)

if __name__ == "__main__":
    cli()
