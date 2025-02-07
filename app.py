import os
import json
import subprocess
from flask import Flask, request, jsonify
from jinja2 import Environment, FileSystemLoader
from flask_cors import CORS

app = Flask(__name__)

## Cross origin resource sharing configuration for flask api
CORS(app)  

## Loading templates from templates folder
env = Environment(loader=FileSystemLoader("templates"))

TERRAFORM_DIR = "terraform"
ANSIBLE_DIR = "ansible"


## Function to execute shell commands
def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)


# API Endpoint to generate Terraform and Ansible scripts
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid request, no data provided"}), 400

        # Extract parameters
        postgres_version = data.get("postgres_version", "14")
        instance_type = data.get("instance_type", "t2.medium")
        num_replicas = data.get("num_replicas", 1)
        max_connections = data.get("max_connections", 200)
        shared_buffers = data.get("shared_buffers", "256MB")

        # Generate Terraform file from template
        terraform_template = env.get_template("main.tf.j2")
        terraform_config = terraform_template.render(
            instance_type=instance_type,
            num_replicas=num_replicas
        )

        os.makedirs(TERRAFORM_DIR, exist_ok=True)
        with open(os.path.join(TERRAFORM_DIR, "main.tf"), "w") as f:
            f.write(terraform_config)

        return jsonify({"message": "Terraform and Ansible configurations generated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Endpoint to run Terraform plan
@app.route("/plan", methods=["POST"])
def terraform_plan():
    # Ensure the plans directory exists
    plans_dir = os.path.join(TERRAFORM_DIR, "plans")
    os.makedirs(plans_dir, exist_ok=True)

    # Run terraform init and plan
    stdout, stderr = run_command("terraform init && terraform plan -out=plan.tfplan", cwd=TERRAFORM_DIR)
    
    if stderr:
        return jsonify({"error": stderr}), 500

    # Save the plan output to a file
    plan_output_file = os.path.join(plans_dir, "plan_output.txt")
    with open(plan_output_file, "w") as f:
        f.write(stdout)

    return jsonify({
        "message": "Terraform plan executed successfully",
        "output": stdout,
        "plan_file": os.path.join(plans_dir, "plan.tfplan"),
        "plan_output_file": plan_output_file
    })

# API Endpoint to apply Terraform (provision AWS related infrastructure)
@app.route("/apply", methods=["POST"])
def terraform_apply():
    try:
        # Run terraform apply
        stdout, stderr = run_command("terraform apply -auto-approve", cwd=TERRAFORM_DIR)
        if stderr:
            return jsonify({"error": stderr}), 500

        return jsonify({"output": stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/configure", methods=["POST"])
def ansible_playbook():
    try:
        # Fetch Terraform outputs
        output_stdout, output_stderr = run_command("terraform output -json", cwd=TERRAFORM_DIR)
        if output_stderr:
            return jsonify({"error": f"Failed to fetch Terraform outputs: {output_stderr}"}), 500

        # Parse Terraform outputs
        outputs = json.loads(output_stdout)
        primary_ip = outputs["primary_ip"]["value"]
        replica_ips = outputs["replica_ips"]["value"]

        # Update Ansible inventory with the fetched IPs
        inventory_template = env.get_template("inventory.j2")
        inventory_content = inventory_template.render(
            primary_ip=primary_ip,
            replica_ips=replica_ips
        )

        # Write the updated inventory file
        with open(os.path.join(ANSIBLE_DIR, "inventory.ini"), "w") as f:
            f.write(inventory_content)

        # Run the Ansible playbook
        stdout, stderr = run_command("ansible-playbook playbook.yml -i inventory.ini", cwd=ANSIBLE_DIR)
        if stderr:
            return jsonify({"error": f"Ansible playbook failed: {stderr}"}), 500

        return jsonify({
            "message": "Ansible playbook executed successfully",
            "output": stdout,
            "primary_ip": primary_ip,
            "replica_ips": replica_ips
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Health Check Endpoint
@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "API is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)