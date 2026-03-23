output "cluster_name" {
  value = google_container_cluster.invoiceflow.name
}

output "cluster_location" {
  value = google_container_cluster.invoiceflow.location
}

output "kubectl_command" {
  value = "gcloud container clusters get-credentials ${google_container_cluster.invoiceflow.name} --region ${var.region} --project ${var.project_id}"
}