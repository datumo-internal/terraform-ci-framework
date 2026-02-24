# Chapter 2: Data Ingestion & Orchestration

### Verification (Manual Step)

Congratulations, your infrastructure foundation is ready! Now prove that you can manage it manually before automating further.

1. Log in to the **Azure Portal**.
2. Navigate to the Resource Group created by Terraform.
3. Click on the newly created **Storage Account** (name starts with `st...`).
4. In the left menu, select **Containers** (under Data storage).
5. Click **+ Container**.
6. Name it: `manual-verification-done`
7. Click **Create**.

*Note: The automated check script will verify if the resource group exists to proceed to Chapter 2.*

### 1. Azure Data Factory (The Engine)
**Azure Data Factory (ADF)** is a cloud-based data integration service.
Imagine ADF as a **pipeline system** or a conveyor belt in a factory. 
* **It does not store data:** ADF is not a database. It simply manages the flow.
* **Orchestrator:** It connects to a source (e.g., your Storage Account), optionally transforms the data, and deposits it into a destination.
* **Low-Code:** It provides a visual interface where you design processes by dragging and dropping blocks, rather than writing complex code from scratch.

### 2. Managed Identity (Digital ID Card) 
In the Terraform code for this chapter, you will see a variable regarding identity type.
* **The Old Way:** Traditional applications connect to databases using a login and password stored in configuration files. This creates a massive security risk (credential theft).
* **The Modern Way (Managed Identity):** We enable **System Assigned Managed Identity**. This gives our Data Factory its own "Digital ID Card" in Azure Active Directory.
* **The Benefit:** ADF can now "introduce itself" to other services (like Key Vault) as a trusted entity. We grant permissions to the *Factory itself*, eliminating the need to type any passwords in our code.

---

## Self-Study & Documentation
Before attempting the quiz, familiarize yourself with the following concepts using official Microsoft documentation:

* **What is ADF?** [Introduction to Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/introduction)
* **Compute:** [Integration Runtime in Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/concepts-integration-runtime)

---

## Theoretical Task
You are the Lead Data Engineer. You need to define the security posture and identity management for the ETL process.
### Instructions
Mark the correct answer by placing an `x` inside the brackets, e.g., `[x]`.

**Task 1: Network Access (Public vs Private)**
Do we expose the Data Factory to the public internet?
- [ ] A) `true` 
- [ ] B) `false`
- [ ] C) `vpn_only`
- [ ] D) `auto_resolve`

**Task 2: Managed Identity (Authentication)**
How should ADF identify itself to other services (like Azure SQL or Blob Storage)?
- [ ] A) `SystemAssigned` - Azure automatically creates and manages the factory's "ID card".
- [ ] B) `UserAssigned` - We manually create an identity and assign it to the factory.
- [ ] C) `ServicePrincipal` - Legacy method using Client ID and Secret.
- [ ] D) `None` - No identity (We will have to type passwords manually - bad practice).

**Task 3: Compute Engine (Integration Runtime)**
Which compute engine is used by default to copy data between cloud services?
- [ ] A) `AutoResolveIntegrationRuntime` - Serverless, managed by Azure.
- [ ] B) `SelfHostedIntegrationRuntime` - Installed on a VM (for on-premise access).
- [ ] C) `SSIS-IR` - Dedicated cluster for legacy SQL Server packages.
- [ ] D) `Databricks-Cluster` - Spark engine for heavy processing.

**Task 4: Triggers (Automation)**
We need to run the pipeline every time a new file lands in the Storage Account. Which trigger type should we use?
- [ ] A) `ScheduleTrigger` - Runs on a clock (e.g., every day at 8 AM).
- [ ] B) `TumblingWindowTrigger` - Runs for specific time slices with backfill support.
- [ ] C) `BlobEventsTrigger` - Reacts immediately when a file is created or deleted.
- [ ] D) `ManualTrigger` - Requires a human to click "Debug".
