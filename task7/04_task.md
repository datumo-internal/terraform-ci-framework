# Chapter 4: Data Warehouse (Synapse Analytics)

### Verification (Manual Step: Incident Response)

**Scenario:** Monitoring is not just about collecting logs; it is about notifying people when things break. Before we deploy automated alert rules via Terraform, you must manually create an "Action Group" – a contact list for the support team.

**Your Mission:**
1. Log in to the **Azure Portal**.
2. In the search bar, type **Monitor** and open the service.
3. In the left menu, select **Alerts**, then click **Action groups** in the top menu.
4. Click **+ Create**.
5. Settings:
   * **Resource Group:** Select your course group (e.g., `rg-course-<your_id>-ch1`).
   * **Region:** Global (default).
   * **Action group name:** `ag-support-email` (Crucial! The script looks for this exact name).
   * **Display name:** `Support`.
6. Go to the **Notifications** tab:
   * **Notification type:** Email/SMS message/Push/Voice.
   * **Name:** `MyEmail`.
   * **Email:** Enter your own email address.
7. Click **Review + create** -> **Create**.

Only after you create this group will the Pipeline allow you to proceed to Chapter 4. The system checks if `ag-support-email` exists in your resource group.

## Introduction
It is time for the analytical heart of our platform. We will deploy **Azure Synapse Analytics**, which will serve as the storage and processing engine for our refined data.
You need to make decisions regarding compute power and data redundancy (resilience to regional failures).

* **Pricing Tier & DWU (Data Warehouse Units):** A cloud data warehouse doesn't have a "CPU" in the traditional sense. Its compute power is measured in DWUs.
  * **Tier:** This is the selected service level.
  * **DW100c:** The lowest tier. It is cheap and perfect for learning or small datasets.
  * **DW3000c:** An Enterprise tier. It provides massive compute power but costs thousands of dollars per month. As an Architect, you must perfectly match the Tier to the client's budget. Choosing a tier that is too high is the most common mistake that ruins cloud project budgets.
* **Redundancy (LRS vs. GRS):** Under the hood, the data warehouse stores its files on a hidden Storage Account. You must decide whether this data should be copied to another geographic region (**GRS** - Geo-Redundant Storage) in case of a regional disaster, or if a local copy is sufficient (**LRS** - Locally Redundant Storage).

---

## Self-Study & Documentation
If you want to master Azure Synapse Analytics, these official Microsoft resources explain the core concepts in detail:

* **[What is Azure Synapse Analytics? (Overview)](https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is)**
*The official introduction to the service. Learn how Synapse bridges the gap between traditional enterprise data warehousing and Big Data analytics.*

* **[Massively Parallel Processing (MPP) Architecture](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/massively-parallel-processing-mpp-architecture)**
*Discover exactly how Synapse distributes queries across compute nodes to process petabytes of data in seconds.*

* **[Synapse Workspace Access Control & Security](https://learn.microsoft.com/en-us/azure/synapse-analytics/security/synapse-workspace-access-control-overview)**
*Understand the security model. Discover why we had to manually set the Entra ID Admin and how permissions work between Synapse Studio, SQL pools, and Managed Identities (like our Data Factory).*

## Theoretical Task
As an Architect, you must balance performance against budget. Mark the correct answer by placing an **x** inside the brackets, e.g., `[x]`.

**Task 1: Warehouse Scaling (Compute Power)**
What performance level (Data Warehouse Units - DWU) should we assign for the starting Development environment?
- [ ] A) `DW100c`
- [ ] B) `DW3000c`
- [ ] C) `Serverless`
- [ ] D) `DW500c`

**Task 2: Data Lake Redundancy (Storage)**
Synapse stores its system files on a dedicated Storage Account. Should this data be copied to another geographic region?
- [ ] A) `LRS`
- [ ] B) `GRS`
- [ ] C) `ZRS`
- [ ] D) `RA-GRS`

**Task 3: Architecture (MPP)**
Synapse Dedicated SQL Pool is an MPP (Massively Parallel Processing) system. What does this mean?
- [ ] A) It distributes data and query processing across multiple compute nodes working together.
- [ ] B) It runs on a single, very powerful virtual machine.
- [ ] C) It is a NoSQL database designed for unstructured JSON documents.
- [ ] D) It is an in-memory cache system like Redis.

**Task 4: Networking (Firewall)**
To allow our Data Factory to connect to this Synapse Workspace, what networking rule must be applied?
- [ ] A) Allow Azure services and resources to access this workspace (`0.0.0.0` rule).
- [ ] B) Open port 80 (HTTP) to the entire internet.
- [ ] C) Disable the Firewall completely (Unsafe).
- [ ] D) Connect via VPN only (Too complex for this course).

