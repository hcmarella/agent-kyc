#!/bin/bash
set -e

echo "===== 1. Docker check ====="
docker info >/dev/null
echo "Docker is running"

echo "===== 2. Kubernetes context ====="
kubectl config current-context
kubectl get nodes

echo "===== 3. Rebuild local image if needed ====="
if ! docker images | grep -q "agent-kyc"; then
  echo "agent-kyc image missing. Building..."
  docker build -t agent-kyc:local .
else
  echo "agent-kyc image exists"
fi

echo "===== 4. Create namespaces ====="
for ns in agent-dev agent-sit agent-sat agent-prod argocd monitoring; do
  kubectl create namespace $ns --dry-run=client -o yaml | kubectl apply -f -
done

echo "===== 4B. Clean unmanaged app objects ====="
for ns in agent-dev agent-sit agent-sat agent-prod; do
  kubectl delete deployment agent-kyc -n $ns --ignore-not-found
  kubectl delete svc agent-kyc-svc -n $ns --ignore-not-found
  kubectl delete configmap agent-kyc-config -n $ns --ignore-not-found
  kubectl delete secret agent-kyc-secret -n $ns --ignore-not-found
done

echo "===== 5. Deploy Helm apps ====="
helm upgrade --install agent-kyc-dev ./helm/agent-kyc -f environments/dev/values.yaml -n agent-dev
helm upgrade --install agent-kyc-sit ./helm/agent-kyc -f environments/sit/values.yaml -n agent-sit
helm upgrade --install agent-kyc-sat ./helm/agent-kyc -f environments/sat/values.yaml -n agent-sat
helm upgrade --install agent-kyc-prod ./helm/agent-kyc -f environments/prod/values.yaml -n agent-prod

echo "===== 6. Install/verify Argo CD ====="
if ! kubectl get deployment argocd-server -n argocd >/dev/null 2>&1; then
  kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
else
  echo "Argo CD already installed"
fi

echo "===== 7. Install/verify Grafana/Prometheus ====="
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

if ! helm list -n monitoring | grep -q monitoring; then
  helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring
else
  echo "Monitoring stack already installed"
fi

echo "===== 8. Apply Argo apps if files exist ====="
for app in dev sit sat prod; do
  if [ -f "argocd/app-$app.yaml" ]; then
    kubectl apply -f argocd/app-$app.yaml
  fi
done

echo "===== 9. Status ====="
kubectl get pods -n agent-dev
kubectl get pods -n agent-sit
kubectl get pods -n agent-sat
kubectl get pods -n agent-prod
kubectl get pods -n argocd
kubectl get pods -n monitoring

echo "===== Done ====="
echo "Run port-forward commands in separate terminals:"
echo "Argo CD:  kubectl port-forward svc/argocd-server -n argocd 8088:443"
echo "Grafana:  kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80"
echo "DEV API:  kubectl port-forward svc/agent-kyc-svc -n agent-dev 8081:80"
