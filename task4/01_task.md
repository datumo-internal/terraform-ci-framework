# Chapter 1: Foundations – Landing Zone & Security

## Introduction
Every Data Engineering project begins with two fundamental questions: "Where do we store the files?" and "Where do we keep the secrets?". In an Enterprise environment, we must strictly separate data from credentials.

## Theory
### Resource Group
Think of a **Resource Group** as a logical container or a folder in Azure. It groups all resources related to a specific solution. It allows you to manage their lifecycle collectively – if you delete the group, everything inside it vanishes. This prevents "zombie resources" from lingering and generating costs after a project ends.

### Azure Data Lake Gen2
This is our warehouse. We enable **Hierarchical Namespace (HNS)** on it. While standard Blob Storage simulates folders using slashes in names, Data Lake Gen2 possesses a true file system. This allows for atomic operations on millions of files, which is crucial for Big Data performance.

### Azure Key Vault
This is our digital safe. The Golden Rule of Cloud Security: **No hardcoded passwords in the code**. Services should retrieve keys and secrets from the Vault on the fly.

* **Security:** [Managed identities for Azure resources](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)

---

## Theoretical Task

You are the Lead Cloud Architect at a Fintech startup serving clients exclusively from the European Union.
You need to make architectural decisions in the form below.
### Instructions
Mark the correct answer by placing an `x` inside the brackets, e.g., `[x]`.

**Task 1: Location (GDPR/Compliance)**
EU law (GDPR) strictly regulates transferring personal data outside the European Economic Area (EEA). We need a region that is compliant and has low latency for our customers.
- [ ] A) `East US`
- [ ] B) `West Europe`
- [ ] C) `China North`
- [ ] D) `Brazil South`

**Task 2: Replication (Redundancy Strategy)**
The data we store are raw logs that can be re-ingested from the source if lost. The project budget is very tight (MVP phase).
- [ ] A) `LRS`
- [ ] B) `GRS`
- [ ] C) `ZRS`
- [ ] D) `RA-GRS`

**Task 3: Naming Convention (Azure Constraints)**
You are defining the name for the Storage Account. Why does Terraform fail if you try to name it simply "data"?
- [ ] A) The name is too short (minimum 5 characters).
- [ ] B) Storage Account names must be globally unique across all of Azure.
- [ ] C) The name must contain at least one uppercase letter.
- [ ] D) "data" is a reserved keyword in Terraform.

**Task 4: Architecture (Data Lake vs Blob)**
Why do we specifically enable "Hierarchical Namespace" for an Analytics workload?
- [ ] A) It is required to use the cool/archive storage tiers.
- [ ] B) It allows us to host a static website on the storage.
- [ ] C) It enables directory-level operations.
- [ ] D) It provides automatic backup to AWS S3.

### How to verify the result?
After a successful `git push`, go to portal.azure.com:
1. Find the Resource Group `rg-course-<your_id>-ch1`.
2. Go to **Storage Account** -> **Configuration**.
3. Verify that **Hierarchical namespace** is set to **Enabled**.
