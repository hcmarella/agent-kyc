#!/bin/bash

echo "===== Kubernetes ====="
kubectl get nodes

echo "===== Helm ====="
helm list -A

echo "===== Argo Apps ====="
kubectl get applications -n argocd || true

echo "===== Pods ====="
kubectl get pods -A

echo "===== Services ====="
kubectl get svc -A

echo "===== API Checks ====="
curl -s http://localhost:8081/health/ready || echo "DEV not reachable"
echo
curl -s http://localhost:8082/health/ready || echo "SIT not reachable"
echo
curl -s http://localhost:8083/health/ready || echo "SAT not reachable"
echo
curl -s http://localhost:8084/health/ready || echo "PROD not reachable"
echo
