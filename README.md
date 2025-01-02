# account-infra
Service Account Infra

Command line to generate serviceaccount,role,rolebinding
```
python3 account.py --domains=example.com
```

Command line to generate only service account, or role, or rolebinding
```
python3 account.py --domains=example.com  --resources=serviceaccount
python3 account.py --domains=example.com  --resources=role
python3 account.py --domains=example.com  --resources=rolebinding
```
