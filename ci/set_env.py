import os
import json
import re
import sys

def parse_markdown_answers(task_dir):
    """
    Scans for any .md file in the task directory and extracts 
    all selected answers marked with [x] or [X].
    """
    answers = []
    if not os.path.exists(task_dir):
        return answers
        
    for file in os.listdir(task_dir):
        if file.endswith(".md"):
            file_path = os.path.join(task_dir, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all patterns like - [x] A or - [X] B
                matches = re.findall(r'-\s*\[[xX]\]\s*([A-Za-z])', content)
                answers.extend(matches)
    return [a.upper() for a in answers]

def main():
    if len(sys.argv) < 2:
        print("[ERROR] No task directory provided.")
        sys.exit(1)

    task_dir = sys.argv[1]
    task_key = os.path.basename(os.path.normpath(task_dir))
    
    # Path to the variable mapping configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "variables.json")
    
    if not os.path.exists(config_path):
        print(f"[INFO] Configuration file {config_path} not found. Skipping environment setup.")
        sys.exit(0)

    with open(config_path, 'r') as f:
        config = json.load(f)

    if task_key not in config:
        print(f"[INFO] No variable mapping defined for '{task_key}' in variables.json. Skipping.")
        sys.exit(0)

    # Extract answers from MD and mappings from JSON
    student_answers = parse_markdown_answers(task_dir)
    mappings = config[task_key].get("mappings", [])

    # GITHUB_ENV is a special file used by GitHub Actions to export environment variables
    env_file = os.environ.get('GITHUB_ENV')
    
    print(f"[INFO] Processing variables for: {task_key}")
    print(f"[INFO] Detected answers: {student_answers}")

    # We only process as many answers as we have mappings for (Task 1 and Task 2)
    for idx, mapping in enumerate(mappings):
        if idx < len(student_answers):
            selected_letter = student_answers[idx]
            
            if selected_letter in mapping:
                variables_to_set = mapping[selected_letter]
                for var_name, var_value in variables_to_set.items():
                    output_line = f"{var_name}={var_value}"
                    print(f"   [EXPORT] {output_line}")
                    
                    if env_file:
                        with open(env_file, 'a') as f:
                            f.write(output_line + "\n")
            else:
                print(f"   [WARN] Answer '{selected_letter}' has no variable mapping in Step {idx+1}.")

if __name__ == "__main__":
    main()