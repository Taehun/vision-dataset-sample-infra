resource "google_storage_bucket" "dataset" {
  name          = "${var.project_id}-dataset"
  force_destroy = false
  storage_class = "STANDARD"
  location      = "asia-northeast3"
}

resource "google_storage_bucket" "temp" {
  name          = "${var.project_id}-temp"
  force_destroy = false
  storage_class = "STANDARD"
  location      = "asia-northeast3"
}
