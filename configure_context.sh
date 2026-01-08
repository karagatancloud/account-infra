#!/usr/bin/env bash
set -euo pipefail

echo "Setup of the Kubernetes context"

read -p "Project name (example): " PROJECT
PROJECT="${PROJECT:-example}"

read -p "Cluster name (kubernetes): " CLUSTER
CLUSTER="${CLUSTER:-kubernetes}"

read -p "Cluster host (admin.kubernetes.com): " HOST
HOST="${HOST:-admin.kubernetes.com}"

read -p "Cluster ca.crt path (ca.crt): " CA_FILE
CA_FILE="${CA_FILE:-ca.crt}"

if [[ ! -f "$CA_FILE" ]]; then
  echo "Error: CA file $CA_FILE does not exist."
  exit 1
fi

read -p "Token (or path to token file): " TOKEN

if [[ -f "$TOKEN" ]]; then
  echo "Reading token from file: $TOKEN"
  TOKEN="$(<"$TOKEN")"
fi

TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

if [[ -z "$TOKEN" ]]; then
  echo "Error: Token cannot be empty."
  exit 1
fi

KUBECONFIG_PATH="$HOME/.kube/${PROJECT}-config.conf"
mkdir -p "$(dirname "$KUBECONFIG_PATH")"

echo ""
echo "Entered parameters:"
echo "Project:        $PROJECT"
echo "Cluster name:   $CLUSTER"
echo "Cluster host:   $HOST"
echo "CA file:        $CA_FILE"
echo "User name:      $PROJECT-user"
echo "Context name:   $PROJECT-context"
echo "Kubeconfig:     $KUBECONFIG_PATH"
echo ""
read -p "Press Enter to continue..."

kubectl --kubeconfig="$KUBECONFIG_PATH" config set-cluster "$CLUSTER" \
  --server="https://$HOST:6443" \
  --certificate-authority="$CA_FILE" \
  --embed-certs=true

kubectl --kubeconfig="$KUBECONFIG_PATH" config set-credentials "$PROJECT-user" \
  --token="$TOKEN"

kubectl --kubeconfig="$KUBECONFIG_PATH" config set-context "$PROJECT-context" \
  --cluster="$CLUSTER" \
  --user="$PROJECT-user"

kubectl --kubeconfig="$KUBECONFIG_PATH" config use-context "$PROJECT-context"

echo ""
echo "Kubeconfig created at: $KUBECONFIG_PATH"

BASE64_FILE="${KUBECONFIG_PATH}.b64"
base64 < "$KUBECONFIG_PATH" | tr -d '\n' > "$BASE64_FILE"

echo "Base64 version written to: $BASE64_FILE"
echo "Done."
