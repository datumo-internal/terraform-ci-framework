# Chapter 5: Connecting the Dots (Building the Pipeline)

### Verification Step: SQL Permissions (CRITICAL)

Terraform created the infrastructure, but for security reasons, it does not have access inside the database to grant permissions. You **MUST** perform this step manually, otherwise, the pipeline in Chapter 5 will fail with a "Login failed" error.

### Critical Step: Set SQL Administrator

To prevent "Login failed" errors during the next steps, you must manually grant yourself administrative access to the database.

1. Log in to the **[Azure Portal](https://portal.azure.com)**.
2. Navigate to your **Synapse workspace** resource (e.g., `syn-<your_id>-dwh`).
3. In the left-hand menu, under **Settings**, select **Microsoft Entra ID**.
4. Click **Set admin**.
5. Search for and select your own user account (email).
6. Click **Select**, then **Save**.
7. Wait 1-2 minutes for the changes to propagate before running any SQL scripts.

#### Grant Data Factory Access
Now that you are the administrator, you can allow your Azure Data Factory to write data into this warehouse.

1. In the "Overview" section of your Synapse workspace, click **Open Synapse Studio**.
2. Inside Synapse Studio, go to the **Develop** tab (the paper icon on the left) -> **SQL scripts**.
3. Click the **+** icon to add a **New SQL script** -> **Empty script**.
4. **IMPORTANT:** Ensure the "Connect to" dropdown at the top of the script window is set to **`dwh_pool`** (Do NOT use `Built-in`).
5. Paste the SQL code below.
6. **ACTION REQUIRED:** Replace `adf-YOUR_ID-dm-course` with the actual name of your Data Factory (you can find it in the Azure Portal).
7. Click **Run**.

```sql
-- Step 1: Create a user for the Managed Identity (Data Factory)
-- REPLACE 'adf-YOUR_ID-dm-course' WITH YOUR DATA FACTORY NAME.
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'adf-YOUR_ID-dm-course')
BEGIN
    CREATE USER [adf-YOUR_ID-dm-course] FROM EXTERNAL PROVIDER;
END

-- Step 2: Grant Owner permissions (db_owner)
-- REPLACE 'adf-YOUR_ID-dm-course' WITH YOUR DATA FACTORY NAME.
EXEC sp_addrolemember 'db_owner', 'adf-YOUR_ID-dm-course';

-- Query template:
-- IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'adf-janmarek-dm-course')
-- BEGIN
--     CREATE USER [adf-janmarek-dm-course] FROM EXTERNAL PROVIDER;
-- END
-- EXEC sp_addrolemember 'db_owner', 'adf-janmarek-dm-course';
```

#### Create the Target Table
Before Azure Data Factory can copy your data, the destination table must exist in the database with the correct structure.

1. Still inside **Synapse Studio** -> **SQL scripts**, clear the previous script.
2. Paste the following SQL code to create the `Products` table.
3. Ensure you are still connected to **`dwh_pool`** and click **Run**.

```sql
CREATE TABLE dbo.Products (
    [id] INT,
    [name] NVARCHAR(100),
    [category] NVARCHAR(50),
    [brand] NVARCHAR(50),
    [price] DECIMAL(10,2),
    [stock] INT,
    [rating] DECIMAL(3,1),
    [date] DATE
)
WITH (
    DISTRIBUTION = ROUND_ROBIN,
    CLUSTERED COLUMNSTORE INDEX
);
```

### Introduction
Your infrastructure is standing, but the buildings are isolated. As a Data Engineer, you must configure **Azure Data Factory** to securely retrieve data from the **Storage Account** and load it into **Synapse Analytics**.

* **Linked Services:** Azure Data Factory (ADF) acts as an orchestrator—it manages resources but does not store data itself. For ADF to fetch a file from a Storage Account or push data into Synapse, we must define Linked Services. Think of them as connection strings. In our code, we use **Managed Identity**, meaning that instead of hardcoding passwords, ADF introduces itself using its own cloud "digital ID card."
* **RBAC (Role-Based Access Control):** Establishing a network connection is not enough; ADF must have permission to read the files. In this chapter, our Terraform code automatically assigns the `Storage Blob Data Contributor` role to the Data Factory. This is the digital equivalent of handing over the warehouse keys to a specific employee.
* **Pipeline & Activities:** A Pipeline is a logical container for tasks (Activities). We define a pipeline named `PL_Copy_CSV_to_SQL`. It contains a "Copy" activity that executes a classic ETL (Extract, Transform, Load) pattern:
  * **Source:** Retrieves the raw data (CSV format) from the Storage Account.
  * **Sink:** Loads the data into a SQL table inside Synapse Analytics.
* **Retry Policy:** In the cloud, transient network issues are natural. A well-designed system should not completely fail just because of a millisecond network hiccup. In our Terraform code, we define a `retry_count` variable, which specifies exactly how many times the system should attempt to retry the operation before officially reporting an error.

It is time to automate the flow of data.

---

## Self-Study & Documentation
If you want to master the orchestration and data movement in Azure Data Factory, these two official resources are the best place to start:

* **[Pipelines and Activities in Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/concepts-pipelines-activities)**
  *This is the absolute core of ADF. Learn how to group activities into logical pipelines, how datasets work, and how linked services establish secure connections to your data stores.*

* **[Copy Activity in Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview)**
  *We used this exact activity to move our CSV file into the SQL database. Read this to understand how ADF performs high-performance data extraction, transformation, and loading (ETL) under the hood.*

## Theoretical Task
You are configuring the production behavior of the pipeline. Mark the correct answer by placing an **x** inside the brackets, e.g., `[x]`.

**Task 1: Schedule (Trigger Strategy)**
The bank delivers transaction files once a day, at night (batch processing). How often should your pipeline check for and download data?
- [ ] A) `Every 5 minutes` (Real-time emulation).
- [ ] B) `Daily at 02:00 AM` (Batch processing).
- [ ] C) `Manual Trigger` (Requires a human to click every night).
- [ ] D) `Weekly`.

**Task 2: Retry Policy (Resilience)**
The cloud network can be unpredictable. What should your pipeline do if the connection to the database drops for a second during copying?
- [ ] A) `Fail Fast` (Stop immediately and send an error alert).
- [ ] B) `Infinite Retry` (Keep trying forever until the budget runs out).
- [ ] C) `Retry Policy` (Try again a specific number of times, e.g., 3 attempts with a 30s delay).
- [ ] D) `Ignore` (Skip the missing data and mark as success).

**Task 3: Performance (PolyBase Staging)**
We are loading data into Synapse (Data Warehouse). Why did we enable "Staging" in the Copy Activity?
- [ ] A) To make the process slower but safer.
- [ ] B) To use PolyBase, which is the fastest way to load bulk data into Synapse.
- [ ] C) To encrypt the data twice.
- [ ] D) To save a backup copy in a separate folder.

**Task 4: Data Format**
The source file `products.csv` is a semi-structured file. Where do we define the structure (schema) so it fits into the SQL table?
- [ ] A) In the Linked Service.
- [ ] B) In the Dataset (Mapping).
- [ ] C) In the Trigger.
- [ ] D) In the Resource Group.

---

## Practical Task: The Grand Finale

We are entering the level of **Infrastructure as Code**. We are not uploading data manually via the portal. Your Terraform code is designed to automatically seed the Storage Account with the `products.csv` file.

Since Terraform has finished its job (`Apply complete`), it is time to verify if the machine actually works.

### Step A: Verify Data Upload
First, ensure Terraform successfully uploaded the source file to the cloud.
1. Go to the **Azure Portal** and find your **Storage Account** (from Chapter 1).
2. In the left menu, select **Containers** -> **data**.
3. You should see a file named `products.csv`.
   * *If the file is there – Terraform did its transport job.*

### Step B: Trigger the Pipeline
The file is in the warehouse; now we must load it into the database.
1. In the **Azure Portal**, navigate to your **Data Factory** resource.
2. Click **Launch Studio**.
3. In ADF Studio, click the **Author** icon (pencil) on the left.
4. Expand **Pipelines** and click `PL_Copy_CSV_to_SQL`.
5. On the top bar, click **Add trigger** -> **Trigger now**.
6. Confirm by clicking **OK**.

### Step C: Monitor Execution
Now watch the pipeline in action.
1. Click the **Monitor** icon (speedometer) on the left menu.
2. In the "Pipeline runs" table, you should see your process.
3. Wait until the status turns to a green **Succeeded**.
   * *Tip: Use the "Refresh" button on top.*

### Step D: Final Verification (SQL SELECT)
If the Pipeline turned green, the data must be in the table.

**Option 1: Via Synapse Studio**
1. In the Azure Portal, open your **Synapse Workspace**.
2. Click **Open Synapse Studio**.
3. Select the **Data** icon (cylinder) on the left.
4. Expand **Workspace** -> **SQL Database** -> Your Pool (e.g., `dwh_pool`) -> **Tables**.
5. You should see the table `dbo.Products`.
6. Right-click on it -> **New SQL script** -> **Select TOP 100 rows**.
7. Click **Run**.
8. You should see results: `Laptop`, `Mouse`, `Monitor`...

**Option 2: Via Azure Data Studio (Desktop)**
1. Open Azure Data Studio.
2. Connect to the Synapse Server (using the SQL Admin login/password from Chapter 4).
3. Right-click the database -> **New Query**.
4. Run:
```sql
SELECT * FROM dbo.Products;
```