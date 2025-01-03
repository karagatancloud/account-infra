from string import Template
import argparse
import pyunycode

separator = "---"

serviceaccount_t = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ${cos}-${sanitized_domain}-sa
  namespace: ${cos}-${sanitized_domain}
"""

role_t = """
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: full-access-role
  namespace: ${cos}-${sanitized_domain}
rules:
  # Allow management of Secrets
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "create", "update", "delete"]
  # Allow list of custom resource definitions
- apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions"]
  verbs: ["get", "list"]
  # Allow management of Deployments
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of ReplicaSets
- apiGroups: ["apps"]
  resources: ["replicasets"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Pods
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Services
- apiGroups: [""]
  resources: ["services"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Replication Controllers
- apiGroups: [""]
  resources: ["replicationcontrollers"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of DaemonSets
- apiGroups: ["apps"]
  resources: ["daemonsets"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
   # Allow management of StatefulSets
- apiGroups: ["apps"]
  resources: ["statefulsets"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["batch"]
  resources: ["cronjobs"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Ingresses
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Gateways (e.g., Istio or similar)
- apiGroups: ["networking.istio.io"] # Update based on your service mesh (e.g., Istio)
  resources: ["gateways"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  # Allow management of Gateway APIs
- apiGroups: ["gateway.networking.k8s.io"]
  resources: ["gateways", "httproutes", "grpcroutes", "tcproutes", "udproutes"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
"""

rolebinding_t = """
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: full-access-role-binding
  namespace: ${cos}-${sanitized_domain}
subjects:
- kind: ServiceAccount
  name: ${cos}-${sanitized_domain}-sa
  namespace: ${cos}-${sanitized_domain}
roleRef:
  kind: Role
  name: full-access-role
  apiGroup: rbac.authorization.k8s.io
"""


resource_map = {
    "serviceaccount": serviceaccount_t,
    "role": role_t,
    "rolebinding": rolebinding_t
}


def format(tmpl, data):
    return Template(tmpl).safe_substitute(data).strip('\n')


def do_generate(resources, data):

    first = True
    for resource in resources:
        if not first:
            print(separator)

        if resource not in resource_map:
            raise Exception(f"unknown resource '{resource}'")

        print(format(resource_map[resource], data))
        first = False


def parse_tokens(input_str):
    return [x.strip() for x in input_str.split(',')]


def generate(args):

    resources = parse_tokens(args.resources)

    data = {
        "cos": args.cos,
    }

    domain = args.domain
    if domain == None:
        domain = input("Enter domain name: ")

    domain = pyunycode.convert(domain)
    data["domain"] = domain
    data["sanitized_domain"] = domain.replace(".", args.dot)

    outputFile = args.o
    if outputFile != None:
        import sys
        with open(outputFile, 'w') as sys.stdout:
            do_generate(resources, data)
    else:
        do_generate(resources, data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Account',
                    description='Service account generator',
                    epilog='Copyright (C) Karagatan, LLC.')
    parser.add_argument("--domain", type=str, help='domain name')
    parser.add_argument("--cos", type=str, default='prod', help='class of service')
    parser.add_argument("--resources", type=str, default='serviceaccount,role,rolebinding', help='generate type of resource')
    parser.add_argument("--dot", type=str, default='-dot-', help='replace dot to this')
    parser.add_argument("-o", type=str, help='output file name')
    args = parser.parse_args()
    generate(args)
