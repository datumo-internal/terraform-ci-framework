import sys
import subprocess
import re
import time

def run_terraform_plan(tf_dir):
    """
    Regenerates the execution plan. Necessary after deleting resources.
    """
    print("🔄 Regenerating Terraform Plan...")
    cmd = ["terraform", f"-chdir={tf_dir}", "plan", "-input=false", "-out=tfplan"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to regenerate plan:")
        print(result.stderr)
        sys.exit(result.returncode)
    
    print("✅ Plan regenerated successfully.")

def run_terraform_apply(tf_dir):
    """
    Runs 'terraform apply' and returns exit code, stdout, and stderr.
    """
    cmd = ["terraform", f"-chdir={tf_dir}", "apply", "-auto-approve", "-input=false", "tfplan"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def delete_azure_resource(resource_id):
    """
    Deletes an Azure resource. Handles special Terraform IDs containing pipes '|'.
    """
    # CASE 1: Handle Terraform-specific IDs (e.g., Diagnostic Settings: ParentID|ChildName)
    if "|" in resource_id:
        print(f"ℹ️ Detected Terraform-specific ID (with '|'). Splitting...")
        try:
            parent_id, child_name = resource_id.split("|")
            
            # Use 'az monitor' for diagnostic settings (most common cause of this error)
            print(f"🧹 AUTO-FIX: Deleting Diagnostic Setting '{child_name}'...")
            cmd = [
                "az", "monitor", "diagnostic-settings", "delete",
                "--resource", parent_id,
                "--name", child_name
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return # Exit function on success
        except Exception as e:
            print(f"⚠️ Failed to delete via 'az monitor'. Falling back to generic delete. Error: {e}")

    # CASE 2: Standard Azure Resource ID
    print(f"🧹 AUTO-FIX: Deleting standard resource: {resource_id}")
    cmd = ["az", "resource", "delete", "--ids", resource_id, "--verbose"]
    
    # We allow this to fail (check=False) to avoid crashing the whole script if resource is already gone
    subprocess.run(cmd, check=False)

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_state.py <tf_dir>")
        sys.exit(1)

    tf_dir = sys.argv[1]
    max_retries = 3
    
    for attempt in range(max_retries):
        print(f"🚀 Terraform Apply: Attempt {attempt + 1}/{max_retries}...")
        
        code, out, err = run_terraform_apply(tf_dir)
        print(out)
        print(err)

        if code == 0:
            print("✅ Terraform Apply finished successfully!")
            sys.exit(0)
        
        # Regex to capture the ID causing the conflict
        match = re.search(r'ID\s+"(/subscriptions/[^"]+)"\s+already exists', err)
        
        if match:
            conflict_id = match.group(1)
            print(f"⚠️ State Conflict Detected! Resource exists in Azure but not in Terraform state.")
            
            try:
                # 1. Attempt to delete the resource (Now with support for '|' IDs)
                delete_azure_resource(conflict_id)
                
                print("⏳ Waiting 10s for Azure API consistency...")
                time.sleep(10)
                
                # 2. Regenerate plan because the Azure state has changed
                run_terraform_plan(tf_dir)
                
                # 3. Retry loop
                continue
            except Exception as e:
                print(f"❌ Failed to resolve conflict: {e}")
                sys.exit(code)
        else:
            print("❌ Critical Terraform error (unrelated to state conflict).")
            sys.exit(code)

    print("❌ Max retries exceeded. Could not auto-resolve conflicts.")
    sys.exit(1)

if __name__ == "__main__":
    main()