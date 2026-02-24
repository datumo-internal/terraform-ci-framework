# Chapter 3: Big Brother – Observability & Monitoring

### Verification (Manual Step: SecOps Role)

**Educational Goal:** In large Enterprise environments, Terraform often lacks permissions to create high-privilege identities. This must be done manually by a Security Operator (SecOps) before deployment. You are now acting in this role.

Your Terraform code expects a specific identity to exist to pass the pre-flight checks.

**Your Mission:**
1. Log in to the **Azure Portal**.
2. In the top search bar, type **Managed Identities** and select the service.
3. Click **+ Create**.
4. Settings:
   * **Resource Group:** Select your course group (e.g., `rg-course-<your_id>-ch1`).
   * **Region:** Same as your other resources (e.g., West Europe).
   * **Name:** `id-adf-student` (Must contain "id-adf" in the name!).
5. Click **Review + create** -> **Create**.

The automated pipeline script (`check_manual_steps.py`) will check if a User Assigned Identity with "id-adf" in its name exists in your resource group. Only then will it allow Terraform to run.

## Introduction
To keep a system healthy, we must know exactly what is happening inside it. In this chapter, we will deploy a **Log Analytics Workspace** – the central brain for logs where telemetry from Data Factory, Storage, and other services will flow.

## Theoretical Task
As a DevOps Engineer, you must balance the cost of storing logs against security requirements. Mark the correct answer by placing an **x** inside the brackets, e.g., `[x]`.

## Self-Study & Documentation
If you want to dive deeper into how Azure handles observability, check out the official Microsoft documentation:

* **[Log Analytics Workspace Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-workspace-overview)**
  *Read about the architecture, how data is structured, and how Azure Monitor securely stores your telemetry.*

* **[Diagnostic Settings in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/diagnostic-settings)**
  *Learn how the "wiring" works under the hood when you connect Azure services (like Data Factory) to your log database.*

**Task 1: Log Retention (Cost Management)**
Logs consume disk space in Azure, and storage costs money. How long should we keep the pipeline execution history in a **Development** environment?
- [ ] A) `30` days
- [ ] B) `365` days
- [ ] C) `730` days
- [ ] D) `7` days

**Task 2: Daily Cap (Bill Shock Prevention)**
What happens if Data Factory enters an error loop and generates 100 GB of logs in an hour? The Azure bill will explode. Do you want to set a daily data limit?
- [ ] A) `1` GB
- [ ] B) `0` GB
- [ ] C) `0.02` GB
- [ ] D) `100` GB

**Task 3: Query Language (Knowledge Check)**
To analyze logs in Azure Monitor (Log Analytics), which query language must you use?
- [ ] A) `KQL` (Kusto Query Language)
- [ ] B) `SQL` (Standard Query Language)
- [ ] C) `Python`
- [ ] D) `Gremlin`

**Task 4: Alerting Logic (Architecture)**
When an alert fires (e.g., "Pipeline Failed"), where should Azure send the notification?
- [ ] A) `ActionGroup`
- [ ] B) `HardcodedEmail`
- [ ] C) `AzureAD`
- [ ] D) `LocalHost`

