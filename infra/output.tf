output "project_id" {
  value       = var.project_id
  description = "GCP Project ID"
}

output "region" {
  value       = var.region
  description = "GCP Region"
}

output "bucket" {
  value       = google_storage_bucket.dataset.name
  description = "GCS Bucket Name"
}

output "topic" {
  value       = google_pubsub_topic.topic.name
  description = "Pub/Sub Topic Name"
}
