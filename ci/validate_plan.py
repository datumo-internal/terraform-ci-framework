import json
import sys
import os
from pathlib import Path

def write_summary(text):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def collect_planned_resources(plan: dict) -> dict:
    """Collects all resources that WILL exist after apply."""
    resources = {}
    root_module = plan.get("planned_values", {}).get("root_module", {})
    
    def extract_from_module(module):
        for resource in module.get("resources", []):
            type_name = resource.get("type")
            name = resource.get("name")
            values = resource.get("values", {})
            simple_key = f"{type_name}.{name}"
            resources[simple_key] = values

        for child in module.get("child_modules", []):
            extract_from_module(child)

    extract_from_module(root_module)
    return resources

def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: validate_plan.py <tf_dir> <plan_json_path> <answers_json_path>")
        return 2

    tf_dir = sys.argv[1]
    plan_path = Path(sys.argv[2])
    answers_path = Path(sys.argv[3])

    try:
        plan = load_json(plan_path)
        answers = load_json(answers_path)
    except Exception as e:
        print(f"ERROR loading files: {e}")
        return 2

    if tf_dir not in answers:
        print(f"[INFO] No validation rules for '{tf_dir}'. Skipping.")
        return 0

    spec = answers[tf_dir]
    required_resources = set(spec.get("resources", []) + spec.get("create", []))
    expected_attributes = spec.get("attributes", {})

    actual_resources_map = collect_planned_resources(plan)
    actual_resources_keys = set(actual_resources_map.keys())

    errors = []

    # Check 1: Existence
    missing = required_resources - actual_resources_keys
    if missing:
        errors.append(f"Missing resources in plan: {sorted(missing)}")

    # Check 2: Attributes
    for res_key, required_params in expected_attributes.items():
        if res_key not in actual_resources_map:
            continue

        actual_params = actual_resources_map[res_key]
        for param_key, param_val in required_params.items():
            real_val = actual_params.get(param_key)
            # Use string comparison to avoid type mismatch (int vs str)
            if str(real_val) != str(param_val):
                errors.append(f"Attribute mismatch in {res_key}: {param_key} expected '{param_val}', got '{real_val}'")

    summary_lines = [f"## 🏗️ Terraform Plan Verification: {tf_dir}"]

    if errors:
        print("❌ Plan validation failed")
        summary_lines.append("### Status: **FAILED** ❌")
        for e in errors:
            print(f"- {e}")
            summary_lines.append(f"- 🔴 {e}")
        
        write_summary("\n".join(summary_lines))
        return 1

    print("✅ Plan validation passed")
    summary_lines.append("### Status: **PASSED** ✅")
    summary_lines.append(f"- **Verified**: {len(required_resources)} resources")
    
    if len(required_resources) > 0:
        summary_lines.append("\n<details><summary>Resource List</summary>\n")
        for r in required_resources:
            summary_lines.append(f"- {r}")
        summary_lines.append("\n</details>")

    write_summary("\n".join(summary_lines))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())