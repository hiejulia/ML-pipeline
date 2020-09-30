- Create secrets `.env`
    - `kubectl create secret generic example-api --from-env-file=secrets.env`
- Run and test app in k8s cluster locally  
- Jenkins 

- Minikube 
    - default context 
        - kubectl config use-context minikube `kubectl config use-context minikube`

- kafka in k8s 
    - kafka namespace 
- helm 
    - `helm repo add bitnami https://charts.bitnami.com/bitnami`
    - kubectl create ns redis
    - helm upgrade \
        --install --atomic --timeout 120s --namespace redis \
        --set cluster.enabled=false \
        --set password=redis \
        --set master.persistence.enabled=false \
        redis bitnami/redis

- Deploy 
    - ./kubernetes.yaml.template.sh | kubectl apply -f -]
    - IMAGE_TAG=latest ./kubernetes.yaml.template.sh | kubectl apply -f -