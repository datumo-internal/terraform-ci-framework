import json
import os
import sys

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.load(f)
        # YAML fallback - prosty parser dla list
        import re
        content = f.read()
        config = {}
        current_key = None
        for line in content.splitlines():
            m = re.match(r"^(\w+):\s*$", line)
            if m:
                current_key = m.group(1)
                config[current_key] = []
            elif current_key and line.strip().startswith("- "):
                config[current_key].append(line.strip()[2:].strip())
        return config

def main():
    if len(sys.argv) < 2:
        print("Usage: which_checks.py <task_dir>")
        sys.exit(1)

    task_dir = sys.argv[1]
    task_name = os.path.basename(os.path.normpath(task_dir))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "tasks_config.yml")
    if not os.path.exists(config_path):
        config_path = os.path.join(script_dir, "tasks_config.json")

    if not os.path.exists(config_path):
        # Brak configu = uruchom wszystko (backward compatibility)
        print("run_quiz=true")
        print("run_plan=true")
        print("run_manual=true")
        return

    config = load_config(config_path)

    plan_tasks = set(config.get("plan", []))
    quiz_tasks = set(config.get("quiz", []))
    manual_tasks = set(config.get("manual", []))

    run_quiz = task_name in quiz_tasks
    run_plan = task_name in plan_tasks
    run_manual = task_name in manual_tasks

    # Wypisz do stdout - GitHub Actions może to przechwycić
    print(f"run_quiz={str(run_quiz).lower()}")
    print(f"run_plan={str(run_plan).lower()}")
    print(f"run_manual={str(run_manual).lower()}")


if __name__ == "__main__":
    main()
