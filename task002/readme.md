# Task 2: Variables

## Goal
In this task, you will make your code more professional. Instead of hardcoding names in the `main.tf` file, you will move them into variables. In Terraform, variables are **defined** separately from their **values** — values are provided in a `.tfvars` file, not assigned in the variable definition like in programming languages.

## Steps to complete
1. **Create a `variables.tf` file**: Define two variables in it: `resource_group_name` and `location` (type `string`). Do not use `default` — you will provide the values in a separate file.
2. **Create a `terraform.tfvars` file**: Put the variable values in it — `resource_group_name = "rg-szkolenie-terraform-02"` and `location = "westeurope"`. Terraform will automatically load this file during `plan` and `apply`.
3. **Use the variables in `main.tf`**: For resource group use locals and for location you can use variable

## What do you need to achieve?
Your infrastructure should remain the same, but the `main.tf` file must not contain the literal values "westeurope" or "rg-szkolenie-terraform-02". The values must be in `terraform.tfvars`, not in `variables.tf`.

> **Tip:** Use the `terraform.tfvars.example` file as a template — copy it to `terraform.tfvars` and fill in the values.



## Additionally
After you solve the task, go through `task002_quiz.md`.