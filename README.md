# Course CI/CD Framework Template

This repository serves as a foundation for building automated, self-validating Cloud and DevOps courses. It is designed for course creators and developers who want to build interactive training environments where student submissions are automatically graded via GitHub Actions.

The framework acts as an automated reviewer, verifying infrastructure code, checking markdown-based quiz answers, and ensuring students have completed specific manual actions in the cloud.

## How it Works

The CI/CD pipeline supports three distinct types of automated validations:

1. **Terraform Plan Validation:** Runs `terraform plan`, parses the JSON output, and strictly verifies if the student is creating the exact resources with the required attributes.
2. **Quiz Verification:** Scans markdown files in the task directory for selected checkboxes (e.g., `- [x] A`) and compares them against a predefined answer key.
3. **Manual Cloud Verification:** Uses the Azure CLI to query the student's actual Azure environment (e.g., verifying if a specific Storage Account or Resource Group was manually created).

## Directory Structure

* `.github/workflows/` - Contains the GitHub Actions pipelines (`terraform.yml` for PR validation and `terraform-auto-destroy.yml` for nightly cleanup).
* `ci/` - The Python-based CI/CD engine containing validation scripts and configuration files.
* `task*/` - Directories containing the actual course content and student working areas.

## Configuring Task Validations (The Router)

Not every chapter requires a Terraform deployment, and not every chapter has a quiz. You control exactly what pipeline steps run for which folder using the `ci/tasks_config.yml` file.

If a folder is listed under a specific key, the pipeline will run that check. If it's not listed, the check is skipped.

## Defining the Rules

As a course creator, you define the grading logic using JSON files located in the `ci/` directory:

* `ci/quiz_answers.json`: Maps the task folder name to an array of correct answer letters (e.g., `{"task2": ["A", "C"]}`).
* `ci/answers.json`: Defines the required Terraform resources and specific attributes the student must include in their code.
* `ci/manual_checks.json`: Defines Azure CLI validation rules.

## Setup Instructions for Course Creators

To use this framework for your own course, follow these steps:

### Repository Setup
1. Click "Use this template" on GitHub to generate your own repository.
2. Clone your new repository locally.
3. Replace the `task*` folders with your own course chapters.
4. Update `ci/tasks_config.yml` and the JSON configuration files to match your curriculum.

### Azure Authentication
The automated pipeline requires permissions to access an Azure subscription to verify manual tasks and deploy Terraform code.

1. Create a Service Principal in Microsoft Entra ID with `Contributor` rights to your target subscription.
2. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
3. Add the following Repository Secrets:
   * `ARM_CLIENT_ID`
   * `ARM_CLIENT_SECRET` (The password for your Service Principal)
   * `ARM_TENANT_ID`
   * `ARM_SUBSCRIPTION_ID`

### State Management
The `terraform.yml` pipeline automatically generates an Azure Storage Account and Container for each student (derived from their GitHub username) to store their remote `.tfstate`. You do not need to pre-provision state backends for your students; the pipeline handles this dynamically during the `init` phase.