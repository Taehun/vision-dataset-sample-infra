resource "null_resource" "enable_apis" {
  provisioner "local-exec" {
    command = "gcloud config set project ${var.project_id}; gcloud services enable `cat apis.txt | xargs`"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "gcloud services disable --force `cat apis.txt | xargs`"
  }
}
