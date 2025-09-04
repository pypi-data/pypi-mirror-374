#!/bin/bash
set -euo pipefail

STACK_NAME="ecs-fargate-stack"
SCRIPT_DIR="$(dirname "$0")"
DEFAULT_TEMPLATE="$SCRIPT_DIR/../templates/template-ecs.yaml"

# ================================
# Elegir template
# ================================
echo "Selecciona el template a usar:"
echo "1) Tengo un template propio"
echo "2) Usar template por defecto ($DEFAULT_TEMPLATE)"
read -p "Opción [1/2]: " TEMPLATE_OPTION

if [ "$TEMPLATE_OPTION" == "1" ]; then
  read -p "Ruta del template de CloudFormation: " TEMPLATE_FILE
  if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ El archivo no existe: $TEMPLATE_FILE"
    exit 1
  fi
elif [ "$TEMPLATE_OPTION" == "2" ]; then
  TEMPLATE_FILE="$DEFAULT_TEMPLATE"
  echo "✅ Usando template por defecto: $TEMPLATE_FILE"
else
  echo "❌ Opción inválida"
  exit 1
fi

# ================================
# Elegir región
# ================================
echo "Selecciona la región:"
echo "1) Usar la región actual configurada en AWS CLI"
echo "2) Especificar manualmente"
read -p "Opción [1/2]: " REGION_OPTION

if [ "$REGION_OPTION" == "1" ]; then
  AWS_REGION=$(echo $AWS_REGION)
  if [ -z "$AWS_REGION" ]; then
    echo "❌ No se encontró región configurada en AWS CLI."
    exit 1
  fi
elif [ "$REGION_OPTION" == "2" ]; then
  read -p "Ingresa la región (ej: us-east-1): " AWS_REGION
else
  echo "❌ Opción inválida"
  exit 1
fi

echo "✅ Región seleccionada: $AWS_REGION"

# ================================
# Preguntar imagen
# ================================
read -p "Ingresa la URI completa de la imagen en ECR (ej: 123456789012.dkr.ecr.$AWS_REGION.amazonaws.com/mi-repo:latest): " IMAGE_URI

# ================================
# Elegir VPC, Subnets y Security Group
# ================================
echo "Selecciona cómo configurar red:"
echo "1) Usar recursos por defecto (Default VPC, Subnets y Security Group)"
echo "2) Especificar manualmente"
read -p "Opción [1/2]: " NETWORK_OPTION

if [ "$NETWORK_OPTION" == "1" ]; then
  echo "🔎 Buscando recursos por defecto en $AWS_REGION..."

  # Default VPC
  DEFAULT_VPC=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query "Vpcs[0].VpcId" \
    --region "$AWS_REGION" \
    --output text)

  if [ "$DEFAULT_VPC" == "None" ]; then
    echo "❌ No se encontró VPC por defecto en $AWS_REGION"
    exit 1
  fi
  echo "✅ VPC por defecto: $DEFAULT_VPC"

  # Subnets por defecto
  SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$DEFAULT_VPC" "Name=default-for-az,Values=true" \
    --query "Subnets[*].SubnetId" \
    --region "$AWS_REGION" \
    --output text)

  if [ -z "$SUBNETS" ]; then
    echo "❌ No se encontraron subnets por defecto"
    exit 1
  fi
  echo "✅ Subnets por defecto: $SUBNETS"

  # Security Group por defecto
  SG=$(aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=$DEFAULT_VPC" "Name=group-name,Values=default" \
    --query "SecurityGroups[0].GroupId" \
    --region "$AWS_REGION" \
    --output text)

  if [ "$SG" == "None" ]; then
    echo "❌ No se encontró security group por defecto"
    exit 1
  fi
  echo "✅ Security Group por defecto: $SG"

elif [ "$NETWORK_OPTION" == "2" ]; then
  read -p "Ingresa el VPC ID: " VPC_ID
  read -p "Ingresa los Subnet IDs (separados por coma): " SUBNET_IDS
  read -p "Ingresa el Security Group ID: " SG

  DEFAULT_VPC="$VPC_ID"
  SUBNETS="$SUBNET_IDS"
else
  echo "❌ Opción inválida"
  exit 1
fi

# ================================
# Deploy CloudFormation
# ================================
echo "🚀 Desplegando stack $STACK_NAME con imagen $IMAGE_URI ..."
aws cloudformation deploy \
  --stack-name "$STACK_NAME" \
  --template-file "$TEMPLATE_FILE" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "$AWS_REGION" \
  --parameter-overrides \
    ImageUri="$IMAGE_URI" \
    SubnetIds="$(echo $SUBNETS | tr ' ' ',')" \
    SecurityGroupIds="$SG"

if [ $? -eq 0 ]; then
    echo "✅ Stack desplegado exitosamente."
else
    echo "❌ Error desplegando el stack."
fi
