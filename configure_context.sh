#!/bin/bash

echo "Setup of the Kubernetes context"

# Prompt the project name
read -p "Project name (example): " PROJECT

# Validate the project name
if [[ -z "$PROJECT" ]]; then
  PROJECT="example"
fi

# Prompt the cluster name
read -p "Cluster name (kubernetes): " CLUSTER

# Validate the cluster name
if [[ -z "$CLUSTER" ]]; then
  CLUSTER="example"
fi

# Prompt the cluster name
read -p "Cluster host (admin.kubernetes.com): " HOST

# Validate the cluster name
if [[ -z "$HOST" ]]; then
  HOST="admin.kubernetes.com"
fi

# Prompt the cluster name
read -p "Cluster ca.crt path (ca.crt): " CA_FILE

# Validate the cluster name
if [[ -z "$CA_FILE" ]]; then
  CA_FILE="ca.crt"
fi

# Check if the file exists
if [[ ! -f "$CA_FILE" ]]; then
  echo "Error: CA file $CA_FILE does not exist."
  exit 1
fi

# Prompt the user for the token
read -p "Token: " TOKEN

# Check if the file exists
if [[ -f "$TOKEN" ]]; then
  echo "Token is the file, reading."
  TOKEN=$(<"$TOKEN")
fi

# Trim leading and trailing whitespace from the input
TOKEN=$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# Validate the token is not empty after trimming
if [[ -z "$TOKEN" ]]; then
  echo "Error: Token cannot be empty or whitespace only."
  exit 1
fi

echo "Entered parameters:"
echo "Projectname: $PROJECT"
echo "Cluster name: $CLUSTER"
echo "Cluster host: $HOST"
echo "CA file: $CA_FILE"
echo "Token: $TOKEN"
echo "User name: $PROJECT-user"
echo "Context name: $PROJECT-context"

# Prompt the user to proceed
echo "Press Enter to continue..."
read

echo "Creating cluster"
echo kubectl config set-cluster $CLUSTER \
    --server=https://$HOST:6443 \
    --certificate-authority=ca.crt \
    --embed-certs=true

kubectl config set-cluster $CLUSTER \
    --server=https://$HOST:6443 \
    --certificate-authority=ca.crt \
    --embed-certs=true


echo "Creating user"
echo kubectl config set-credentials $PROJECT-user \
    --token=$TOKEN

kubectl config set-credentials $PROJECT-user \
    --token=$TOKEN

echo "Creating context"
echo kubectl config set-context $PROJECT-context \
    --cluster=$CLUSTER \
    --user=$PROJECT-user

kubectl config set-context $PROJECT-context \
    --cluster=$CLUSTER \
    --user=$PROJECT-user

echo "Use context"
echo kubectl config use-context $PROJECT-context
kubectl config use-context $PROJECT-context

echo ""

echo "Kubernetes config in Base64"
cat ~/.kube/config | base64
