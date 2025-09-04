# Documentación de AWS CloudShell

## ¿Qué es AWS CloudShell?

**AWS CloudShell** es una consola de línea de comandos basada en navegador que te permite interactuar con los recursos de AWS sin necesidad de instalar herramientas en tu máquina local.  
Cuando la abres, se autentica automáticamente con las credenciales de tu cuenta de AWS y te brinda un entorno preconfigurado con utilidades comunes como:

- **AWS CLI**
- **Git**
- **Python, Node.js y PowerShell**
- **Herramientas de red** (`curl`, `wget`, `ping`, etc.)

Además, cuenta con **1 GB de almacenamiento persistente** en tu directorio de inicio (`~/`), lo que significa que los archivos que guardes ahí permanecerán entre sesiones.

---

## Usos básicos de AWS CloudShell

1. **Administración de recursos en AWS**  
   Ejecuta comandos con la AWS CLI para listar, crear o eliminar recursos.  
   ```bash
   aws s3 ls                # Listar buckets de S3
   aws ec2 describe-instances  # Ver instancias EC2
   ````

2. **Automatización con scripts**
   Puedes crear y ejecutar scripts en Bash, Python o PowerShell para automatizar tareas.

   ```bash
   echo "Hola CloudShell" > saludo.txt
   cat saludo.txt
   ```

3. **Pruebas y troubleshooting**
   Revisa conectividad o endpoints usando herramientas ya instaladas:

   ```bash
   curl https://aws.amazon.com
   ping google.com
   ```

4. **Trabajo con repositorios**
   Clona, edita y gestiona repositorios con `git`.

   ```bash
   git clone https://github.com/usuario/repositorio.git
   cd repositorio
   ```

5. **Aprendizaje y práctica**
   Ideal para practicar comandos de AWS sin configurar nada en tu PC.

---

## ¿Cómo acceder a AWS CloudShell?

1. Inicia sesión en la **[Consola de AWS](https://console.aws.amazon.com/)**.
2. En la esquina superior derecha, haz clic en el ícono de **CloudShell** (una terminal con `>_`).
3. Espera unos segundos a que se inicie el entorno.
4. Comienza a ejecutar comandos de inmediato, ya que CloudShell se abre **autenticado con tus credenciales**.

---

## Beneficios de usar AWS CloudShell

* No necesitas instalar ni configurar la AWS CLI en tu equipo.
* Entorno seguro administrado por AWS.
* Persistencia de archivos en `~/` con 1 GB de almacenamiento.
* Soporta múltiples shells: **Bash**, **PowerShell** y **zsh**.
* Acceso inmediato desde cualquier navegador.

---

## Recursos adicionales

* [Documentación oficial de AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html)

# CloudShell CLI

CLI en Python para automatizar tareas en AWS CloudShell como:
- Login en ECR
- Correr imágenes Docker
- Ejecutar tareas ECS con Fargate
- Buscar archivos en diferentes buckets S3

## Instalación
```sh
pip install cloudshell-cli
```