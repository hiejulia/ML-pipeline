#!/usr/bin/env bash
set -euo pipefail

# Variables for the template
INGRESS_HOSTNAME="${INGRESS_HOSTNAME:-"${APP_NAME}.csf"}"

# Tag for the Docker image
if [ -z "${IMAGE_TAG:-}" ]; then
    IMAGE_TAG=$(git rev-parse HEAD)
fi

# Name for the Docker image
if [ -z "${IMAGE_NAME:-}" ]; then
    IMAGE_NAME="/${ORGANISATION}/${APP_NAME}/public/${APP_NAME}"
fi

# Set this flag to disable Kafka authentication
if [ -n "${KAFKA_AUTH_DISABLED:-}" ]; then
    KAFKA_AUTH_DISABLED="true"
else
    KAFKA_AUTH_DISABLED="false"
fi

# The template
cat <<EOF
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
  namespace: ${NAMESPACE}
  annotations:
    kubernetes.io/ingress.class: internal
spec:
  tls:
  - hosts:
    - ${INGRESS_HOSTNAME}
  rules:
  - host: ${INGRESS_HOSTNAME}
    http:
      paths:
      - path: /
        backend:
          serviceName: ${APP_NAME}
          servicePort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
  namespace: ${NAMESPACE}
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    targetPort: 5002
  selector:
    app: ${APP_NAME}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
  namespace: ${NAMESPACE}
spec:
  progressDeadlineSeconds: 30
  replicas: 2
  selector:
    matchLabels:
      app: ${APP_NAME}
  template:
    metadata:
      labels:
        app: ${APP_NAME}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5002"
    spec:
      securityContext:
        runAsUser: 101010
        runAsGroup: 101010
        fsGroup: 101010
      containers:
      - name: ${APP_NAME}
        image: ${IMAGE_NAME}:${IMAGE_TAG}
        ports:
        - name: http
          containerPort: 5002
        resources:
          limits:
            memory: 1Gi
          requests:
            cpu: 200m
            memory: 512Mi
        readinessProbe:
          httpGet:
            path: /health/readiness
            port: 5002
        env:
        - name: API_GATEWAY_HOST
          value: ${INGRESS_HOSTNAME}
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: kafka-endpoints
              key: bootstrap-servers
        - name: LOG_SECURITY_PROTOCOL
          value: ${LOG_SECURITY_PROTOCOL:-"SSL"}
        - name: LOG_SSL_CA_LOCATION
          value: /etc/kafka-client/ca.crt
        - name: LOG_SSL_CERT_LOCATION
          value: /etc/kafka-client/client.crt
        - name: LOG_SSL_KEY_LOCATION
          value: /etc/kafka-client/client.key
        envFrom:
        - secretRef:
            name: ${APP_NAME}
        volumeMounts:
        - name: kafka-client-config
          mountPath: /etc/kafka-client
          readOnly: true
      volumes:
      - name: kafka-client-config
        secret:
          secretName: ${APP_NAME}-kafka-client
          optional: ${KAFKA_AUTH_DISABLED}
      terminationGracePeriodSeconds: 30
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: ${APP_NAME}
              topologyKey: kubernetes.io/hostname
EOF
