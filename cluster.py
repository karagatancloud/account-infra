from string import Template
import argparse
import pyunycode

separator = "---"

clusterrole_t = """
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: crd-read-role
rules:
  - apiGroups: ["apiextensions.k8s.io"]
    resources: ["customresourcedefinitions"]
    verbs: ["get", "list"]
"""

clusterrolebinding_header_t = """
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: crd-read-role-binding
subjects:
"""

clusterrolebinding_entry_t = """
  - kind: ServiceAccount
    name: ${cos}-${sanitized_domain}-sa
    namespace: ${cos}-${sanitized_domain}
"""

clusterrolebinding_footer_t = """
roleRef:
  kind: ClusterRole
  name: crd-read-role
  apiGroup: rbac.authorization.k8s.io
"""


def format(tmpl, **kwargs):
    return Template(tmpl).safe_substitute(kwargs).strip('\n')


def gen_clusterrole(domain_list, data):
    yield clusterrole_t.strip('\n')


def gen_clusterrolebinding(domain_list, data):
    yield clusterrolebinding_header_t.strip('\n')
    dot = data["dot"]
    cos = data["cos"]
    for domain in domain_list:
        if domain != "":
            domain = pyunycode.convert(domain)
            sanitized_domain=domain.replace(".", dot)
            yield format(clusterrolebinding_entry_t, cos=cos, sanitized_domain=sanitized_domain)
    yield clusterrolebinding_footer_t.strip('\n')


def gen_clusterrolebinding_collector(domain_list, data):
    lines = []
    for value in gen_clusterrolebinding(domain_list, data):
        lines.append(value)
    yield "\n".join(lines)


resource_map = {
    "clusterrole": gen_clusterrole,
    "clusterrolebinding": gen_clusterrolebinding_collector
}


def do_generate(resources, domain_list, data):
    first = True
    for resource in resources:

        if resource not in resource_map:
            raise Exception(f"unknown resource '{resource}'")

        generator = resource_map[resource]

        for value in generator(domain_list, data):
            if not first:
                print(separator)
            print(value)
            first = False


def parse_tokens(input_str):
    return [x.strip() for x in input_str.split(',')]


def convert_file_to_comma_separated(file_path):
    with open(file_path, 'r') as file:
        # Read all lines from the file, strip trailing newlines, and skip empty lines
        lines = [line.strip() for line in file.readlines() if line.strip()]
    # Join the non-empty lines with commas
    result = ','.join(lines)
    return result


def generate(args):

    resources = parse_tokens(args.resources)

    data = {
        "cos": args.cos,
        "dot": args.dot
    }

    domain_list = []
    if "clusterrolebinding" in resources:
        domain_list = args.domains
        if domain_list == '' and args.domains_file != '':
            domain_list = convert_file_to_comma_separated(args.domains_file)
        if domain_list == '':
            domain_list = input("Enter comma separated domain list: ")
        domain_list = parse_tokens(domain_list)

    outputFile = args.o
    if outputFile != None:
        import sys
        with open(outputFile, 'w') as sys.stdout:
            do_generate(resources, domain_list, data)
    else:
        do_generate(resources, domain_list, data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Account',
                    description='Service account generator on cluster level',
                    epilog='Copyright (C) Karagatan, LLC.')
    parser.add_argument("--domains", type=str, default='', help='comma separated domain list')
    parser.add_argument("--domains_file", type=str, default='', help='file containing line separated domain list')
    parser.add_argument("--cos", type=str, default='prod', help='class of service')
    parser.add_argument("--resources", type=str, default='clusterrole,clusterrolebinding', help='generate type of resource')
    parser.add_argument("--dot", type=str, default='-dot-', help='replace dot to this')
    parser.add_argument("-o", type=str, help='output file name')
    args = parser.parse_args()
    generate(args)
