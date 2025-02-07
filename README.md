# Flask API for Terraform & Ansible Automation

## Overview
This Flask API is designed to automate the provisioning and configuration of infrastructure using Terraform and Ansible. It provides a set of endpoints to generate configuration files, plan and apply Terraform deployments, and configure the infrastructure using Ansible playbooks. This tool is particularly useful for DevOps teams looking to streamline their infrastructure management processes.

## Prerequisites
Before you get started, make sure you have the following installed:

- **Python 3.x**: The API is built using Python, so you'll need Python 3.x installed.
- **Flask**: The web framework used to build the API.
- **Terraform**: For infrastructure provisioning.
- **Ansible**: For configuration management.
- **AWS CLI**: If you're deploying on AWS, you'll need the AWS CLI configured with your credentials.
- **Jinja2**: Used for rendering configuration templates.
- **Docker** (optional): If you want to containerize the application.

## Installation
1. **Clone the repository**:
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Set up a virtual environment**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration
### Terraform AWS Provider Setup
If you're using AWS, you'll need to configure the AWS provider in your Terraform template (`main.tf.j2`). You can either hardcode your credentials (not recommended for production) or use environment variables.

**Option 1: Hardcode credentials in `main.tf.j2`**:
```hcl
provider "aws" {
  region     = "us-east-1"  # Change as needed
  access_key = "<your-access-key>"
  secret_key = "<your-secret-key>"
}
```

**Option 2: Use environment variables**:
```sh
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
```

## Running the Flask API
To start the Flask server, run:
```sh
python app.py
```
The API will be available at `http://localhost:5000`.

## API Endpoints
### 1. Generate Terraform & Ansible Configurations
**Endpoint:** `POST /generate`
- **Description:** This endpoint generates Terraform and Ansible configuration files based on the user's input.
- **Payload Example:**
  ```json
  {
    "postgres_version": "14",
    "instance_type": "t2.medium",
    "num_replicas": 1,
    "max_connections": 200,
    "shared_buffers": "256MB"
  }
  ```
- **Response:**
  ```json
  {"message": "Terraform and Ansible configurations generated successfully!"}
  ```

### 2. Run Terraform Plan
**Endpoint:** `POST /plan`
- **Description:** This endpoint initializes Terraform and generates an execution plan. It outputs the plan details, which can be reviewed before applying.
- **Response:**
  ```json
  {
    "message": "Terraform plan executed successfully",
    "output": "<Terraform Plan Output>",
    "plan_file": "terraform/plans/plan.tfplan",
    "plan_output_file": "terraform/plans/plan_output.txt"
  }
  ```

### 3. Apply Terraform Configuration
**Endpoint:** `POST /apply`
- **Description:** This endpoint applies the Terraform configuration to provision the infrastructure.
- **Response:**
  ```json
  {"output": "Terraform apply output"}
  ```

### 4. Configure Infrastructure with Ansible
**Endpoint:** `POST /configure`
- **Description:** This endpoint runs Ansible playbooks to configure the provisioned instances.
- **Response:**
  ```json
  {
    "message": "Ansible playbook executed successfully",
    "output": "Ansible output",
    "primary_ip": "<primary-instance-ip>",
    "replica_ips": ["<replica-instance-ip>"]
  }
  ```

### 5. Health Check
**Endpoint:** `GET /status`
- **Description:** A simple health check endpoint to verify that the API is running.
- **Response:**
  ```json
  {"status": "API is running"}
  ```

## Deployment with Docker (Optional)
If you prefer to run the API in a Docker container, you can do so by creating a `Dockerfile`:

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Build and run the Docker container:
```sh
docker build -t flask-terraform-ansible .
docker run -p 5000:5000 flask-terraform-ansible
```

## Conclusion
This Flask API simplifies the process of provisioning and configuring infrastructure using Terraform and Ansible. It’s a powerful tool for automating cloud resource creation and configuration management, making it easier for DevOps teams to manage their infrastructure. Feel free to modify the templates and playbooks to suit your specific needs.

---

This version is written in a more human tone, with less of the rigid structure that often characterizes AI-generated content. It’s designed to be approachable and easy to follow, while still providing all the necessary details.