terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

# 1. Criação do Cluster k3d mapeando a porta do Ingress Traefik
resource "null_resource" "k3d_cluster" {
  provisioner "local-exec" {
    command = "k3d cluster create devops-aula -p 8080:80@loadbalancer --agents 1"
  }
}
# 2. Importação da imagem local para o cluster
resource "null_resource" "import_image" {
  depends_on = [null_resource.k3d_cluster]
  provisioner "local-exec" {
    command = "k3d image import profdiegoluispires/tic-tac-toe:latest -c devops-aula"
  }
}

# 3. Aplicação dos manifestos na pasta k8s/ (ConfigMap, Deployment, Service e Ingress)
resource "null_resource" "deploy_app" {
  depends_on = [null_resource.import_image]
  provisioner "local-exec" {
    command = "kubectl apply -f ${path.module}/k8s/"
  }
}

# 4. Instalação do Prometheus + Grafana via Helm
resource "helm_release" "kube_prometheus_stack" {
  depends_on       = [null_resource.k3d_cluster]
  name             = "monitoring"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
}

# 5. Instalação do Loki + Promtail via Helm
resource "helm_release" "loki_stack" {
  depends_on       = [helm_release.kube_prometheus_stack]
  name             = "loki"
  repository       = "https://grafana.github.io/helm-charts"
  chart            = "loki-stack"
  namespace        = "monitoring"

  set {
    name  = "promtail.enabled"
    value = "true"
  }

  set {
    name  = "grafana.enabled"
    value = "false"
  }
}