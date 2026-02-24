import sys
import subprocess
import json
import os

def run_az_cmd(cmd_list):
    """Executes Azure CLI command and returns JSON output."""
    try:
        # Force JSON output if not present
        if "--output" not in cmd_list and "-o" not in cmd_list:
            cmd_list.extend(["-o", "json"])
            
        result = subprocess.run(
            cmd_list, capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return None

# --- Check Functions ---

def check_container_exists(rg_name, params):
    container_name = params.get('container_name')
    print(f"   [CHECK] Looking for container '{container_name}'...")
    
    # Get the first storage account in the RG
    sa_name_res = run_az_cmd(["az", "storage", "account", "list", "-g", rg_name, "--query", "[0].name"])
    
    if not sa_name_res:
        print(f"   [FAIL] No Storage Account found in {rg_name}.")
        return False
    
    # Check container existence
    cmd = [
        "az", "storage", "container", "exists", 
        "--account-name", sa_name_res, 
        "--name", container_name, 
        "--auth-mode", "login"
    ]
    result = run_az_cmd(cmd)
    
    if result and result.get("exists") is True:
        return True
    return False

def check_resource_exists(rg_name, params):
    """Checks if a resource of a specific type exists with a specific name pattern."""
    r_type = params.get('resource_type')
    name_contains = params.get('name_contains', '')
    print(f"   [CHECK] Looking for resource '{r_type}' containing name '{name_contains}'...")

    # List resources of the specific type in the RG
    resources = run_az_cmd(["az", "resource", "list", "-g", rg_name, "--resource-type", r_type])
    
    if not resources:
        print(f"   [FAIL] No resources of type {r_type} found in {rg_name}.")
        return False
        
    for r in resources:
        if name_contains.lower() in r.get('name', '').lower():
            print(f"   [OK] Found resource: {r.get('name')}")
            return True
            
    print(f"   [FAIL] Resource of type {r_type} with name containing '{name_contains}' not found.")
    return False

# --- Dispatcher ---
# Maps string names from JSON to Python functions
DISPATCHER = {
    "container_exists": check_container_exists,
    "resource_exists": check_resource_exists
}

def main():
    if len(sys.argv) < 3:
        print("Usage: python check_manual.py <task_dir> <student_id>")
        sys.exit(1)

    task_dir = sys.argv[1]
    student_id = sys.argv[2]
    
    # 1. Load Configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "manual_checks.json")

    if not os.path.exists(config_path):
        print(f"[INFO] Configuration file {config_path} not found. Skipping manual checks.")
        sys.exit(0)

    with open(config_path, 'r') as f:
        config = json.load(f)

    # 2. Check if current task has requirements
    # Normalize path (get the last folder name, e.g., 'task5')
    task_key = os.path.basename(os.path.normpath(task_dir))

    if task_key not in config:
        print(f"[INFO] No manual verification defined for {task_key}. Proceeding.")
        sys.exit(0)

    task_config = config[task_key]
    
    # 3. Determine Resource Group Name
    # Defaulting to 'ch1' suffix as per your course structure, unless overridden in JSON
    suffix = task_config.get("rg_suffix", "ch1")
    rg_name = f"rg-course-{student_id}-{suffix}"

    print(f"STARTING MANUAL VERIFICATION FOR: {task_key}")
    print(f"Description: {task_config.get('description', 'Manual Check')}")
    print(f"Target Resource Group: {rg_name}")

    all_passed = True

    # 4. Run Checks
    for check in task_config.get("checks", []):
        check_type = check.get("type")
        handler = DISPATCHER.get(check_type)
        
        if handler:
            if handler(rg_name, check):
                print("   [PASS] Check passed.")
            else:
                print("   [FAIL] Check failed.")
                all_passed = False
        else:
             print(f"   [WARN] Unknown check type: {check_type}")

    if all_passed:
        print("\nRESULT: MANUAL CHECKS PASSED")
        sys.exit(0)
    else:
        print("\nRESULT: MANUAL CHECKS FAILED")
        print("Please complete the required manual steps in the Azure Portal.")
        sys.exit(1)

if __name__ == "__main__":
    main()