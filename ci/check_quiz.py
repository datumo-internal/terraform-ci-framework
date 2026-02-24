import os
import json
import re
import sys

def write_github_summary(text):
    """Writes output to the GitHub Action Step Summary."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def save_quiz_report_for_pr(text):
    """Saves the quiz report to a file to be included in the PR comment later."""
    with open("quiz_summary.md", "w", encoding="utf-8") as f:
        f.write(text)

def parse_markdown_answers(file_path):
    answers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'-\s*\[[xX]\]\s*([A-Za-z])', line)
                if match:
                    answers.append(match.group(1).upper())
    except FileNotFoundError:
        return None
    return answers

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    answers_file = os.path.join(script_dir, 'quiz_answers.json')
    
    if not os.path.exists(answers_file):
        print(f"[ERROR] Configuration file not found: {answers_file}")
        sys.exit(1)

    with open(answers_file, 'r') as f:
        answer_key = json.load(f)

    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = os.getcwd()

    target_folder_name = os.path.basename(os.path.normpath(target_path))

    if target_folder_name not in answer_key:
        print(f"[INFO] No quiz configuration found for '{target_folder_name}'. Skipping.")
        sys.exit(0)

    print(f"[INFO] Checking quiz for: {target_folder_name}")
    
    md_file_path = None
    possible_files = [f for f in os.listdir(target_path) if f.endswith(".md")]
    
    if "instructions.md" in possible_files:
        md_file_path = os.path.join(target_path, "instructions.md")
    elif possible_files:
        md_file_path = os.path.join(target_path, possible_files[0])
    
    if not md_file_path:
        print(f"[ERROR] No .md file found in {target_path}")
        sys.exit(1)

    student_answers = parse_markdown_answers(md_file_path)
    expected_answers = answer_key[target_folder_name]

    # Build Report Table
    # We use #### to make it a sub-header in the PR comment
    summary_report = [f"#### Quiz Details: {target_folder_name}"]
    summary_report.append("| Question | Your Answer | Result |")
    summary_report.append("| :---: | :---: | :--- |")
    
    failed = False
    error_msg = ""

    # Check for count mismatch first
    if len(student_answers) != len(expected_answers):
        failed = True
        if len(student_answers) > len(expected_answers):
            error_msg = f"**Error:** Detected {len(student_answers)} selections, expected {len(expected_answers)}. Too many options selected."
        else:
            error_msg = f"**Error:** Detected {len(student_answers)} selections, expected {len(expected_answers)}. Some questions missed."
        
        print(f"[FAIL] {error_msg}")
        save_quiz_report_for_pr(error_msg)
        write_github_summary(f"### 🛑 Quiz Failed\n{error_msg}")
        sys.exit(1)

    # Check correctness
    correct_count = 0
    for i, (student, expected) in enumerate(zip(student_answers, expected_answers)):
        q_num = i + 1
        if student == expected:
            print(f"[PASS] Q{q_num}: Correct ({student})")
            summary_report.append(f"| {q_num} | **{student}** | ✅ Correct |")
            correct_count += 1
        else:
            print(f"[FAIL] Q{q_num}: Expected {expected}, got {student}")
            summary_report.append(f"| {q_num} | {student} | ❌ **Incorrect** |")
            failed = True

    # Calculate Score
    score_percent = int((correct_count / len(expected_answers)) * 100)
    summary_report.insert(1, f"\n**Score: {score_percent}%** ({correct_count}/{len(expected_answers)})\n")

    report_text = "\n".join(summary_report)
    
    # SAVE REPORT ALWAYS
    save_quiz_report_for_pr(report_text)

    if failed:
        write_github_summary(report_text)
        print("\n[RESULT] Verification FAILED.")
        sys.exit(1)
    else:
        write_github_summary(report_text)
        print("\n[RESULT] Verification PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()