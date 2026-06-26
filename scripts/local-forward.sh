#!/bin/bash

echo "Starting port-forwards..."
echo "Open new terminals if any command blocks."

kubectl port-forward svc/argocd-server -n argocd 8088:443 &
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80 &
kubectl port-forward svc/agent-kyc-svc -n agent-dev 8081:80 &
kubectl port-forward svc/agent-kyc-svc -n agent-sit 8082:80 &
kubectl port-forward svc/agent-kyc-svc -n agent-sat 8083:80 &
kubectl port-forward svc/agent-kyc-svc -n agent-prod 8084:80 &

echo "127.0.0.1 argocd.local grafana.local" | sudo tee -a /etc/hosts
wait
