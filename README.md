# account-infra
Service Account Infra

Command line to generate serviceaccount,role,rolebinding
```
python3 account.py --domains=example.com
```

Command line to generate only service account, or role, or rolebinding
```
python3 account.py --domain=example.com  --resources=serviceaccount
python3 account.py --domain=example.com  --resources=role
python3 account.py --domain=example.com  --resources=rolebinding
```

Create cluster role with binding
```
python3 cluster.py --domains=example.com  
```

Create cluster role binding
```
python3 cluster.py --domains=example.com,anotherdomain.com  --resources=clusterrolebinding
```

Generate token to use in authentication for 90 days
```
kubectl create token prod-example-dot-com-sa -n prod-example-dot-com --duration=2160h
```

Use the token in remote computer
```
kubectl config set-cluster example \
    --server=https://kubernetes.default:6443 \
    --certificate-authority=ca.crt \
    --embed-certs=true

kubectl config set-credentials example-user \
    --token=YOUR_TOKEN_HERE

kubectl config set-context example-context \
    --cluster=example \
    --user=example-user

kubectl config use-context example-context
```
