import os
import json
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'messages.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {
            "course_name": "Cloud Training",
            "technology": "Azure",
            "icons": {"success": "✅", "failure": "❌", "info": "ℹ️", "skipped": "➖", "warning": "⚠️"},
            "steps": {}
        }

    def is_enabled(env_var_name):
        val = os.environ.get(env_var_name, "")
        if not val: return True
        return val.lower() != "false"

    status_quiz = os.environ.get("QUIZ_RESULT", "skipped")
    status_manual = os.environ.get("MANUAL_RESULT", "skipped")
    status_plan = os.environ.get("PLAN_RESULT", "skipped")
    status_apply = os.environ.get("APPLY_RESULT", "skipped")

    run_quiz = is_enabled("RUN_QUIZ")
    run_manual = is_enabled("RUN_MANUAL")
    run_plan = is_enabled("RUN_PLAN")

    event_name = os.environ.get("GITHUB_EVENT_NAME", "pull_request")
    student_id = os.environ.get("STUDENT_ID", "Unknown")
    task_dir = os.environ.get("TASK_DIR", "Unknown Task")

    icons = config.get("icons", {})
    
    # --- MESSAGES (Generic & Professional) ---
    def get_msg(step, status):
        if status == 'success':
            if step == 'quiz': return "All answers are correct."
            if step == 'manual': return "Prerequisites verified."
            if step == 'plan': return "Infrastructure model verified successfully."
            if step == 'apply': return "Ready for deployment."
            return "Success."
        elif status == 'failure':
            if step == 'quiz': return "Incorrect answers detected."
            if step == 'manual': return "Prerequisites missing."
            if step == 'plan': return "Configuration or syntax error."
            return "Validation failed."
        return "-"

    def get_row_data(step_key, status, is_required):
        if not is_required: return None 

        label = step_key.capitalize() 
        
        # --- CUSTOM STEP NAMES ---
        if step_key == "quiz": label = "Quiz Answers Verification"
        if step_key == "manual": label = "Manual Verification"
        if step_key == "plan": label = "Infrastructure Definition"
        if step_key == "apply": label = "Deployment Status"

        icon = icons.get("info", "ℹ️")
        msg = "-"

        if status == 'success':
            icon = icons.get("success", "✅")
            msg = get_msg(step_key, 'success')
        elif status == 'failure':
            icon = icons.get("failure", "❌")
            msg = get_msg(step_key, 'failure')
        elif status == 'skipped':
            icon = icons.get("skipped", "➖")
            msg = "Skipped"
        
        return f"| **{label}** | {icon} | {msg} |"

    table_rows = []

    # 1. Quiz Row
    row_quiz = get_row_data("quiz", status_quiz, run_quiz)
    if row_quiz: table_rows.append(row_quiz)

    # 2. Manual Row
    row_manual = get_row_data("manual", status_manual, run_manual)
    if row_manual: table_rows.append(row_manual)

    # 3. Plan Row
    row_plan = get_row_data("plan", status_plan, run_plan)
    if row_plan: table_rows.append(row_plan)

    # 4. Apply Row (Deployment Status)
    if run_plan: 
        if event_name == "pull_request":
            if status_plan == "success":
                row_apply = f"| **Deployment Status** | ✅ Ready | Infrastructure ready. Merge to deploy. |"
            elif status_plan == "failure":
                row_apply = f"| **Deployment Status** | 🚫 Blocked | Fix configuration errors first. |"
            else:
                row_apply = f"| **Deployment Status** | {icons.get('skipped', '➖')} | Waiting for Plan... |"
        else:
            # Merge/Push Event
            if status_apply == 'success':
                row_apply = f"| **Deployment Status** | {icons.get('success', '✅')} | Resources deployed successfully. |"
            elif status_apply == 'failure':
                row_apply = f"| **Deployment Status** | {icons.get('failure', '❌')} | Deployment failed. |"
            else:
                row_apply = f"| **Deployment Status** | {icons.get('info', 'ℹ️')} | - |"
        
        table_rows.append(row_apply)

    if not table_rows:
        table_rows.append("| **System** | ⚠️ | No checks configured. |")

    main_emoji = icons.get("success", "✅")
    main_title = "Validation Passed"
    is_failure = False
    extra_details = ""

    # --- DETAILS SECTION ---
    if run_quiz and os.path.exists("quiz_summary.md"):
        with open("quiz_summary.md", "r", encoding="utf-8") as qf:
            quiz_content = qf.read()
            
            if status_quiz == 'failure':
                main_emoji = icons.get("failure", "❌")
                main_title = "Quiz Failed"
                is_failure = True
                extra_details += f"\n\n---\n{quiz_content}\n"
            else:
                extra_details += f"\n\n<details><summary>View Quiz Results</summary>\n\n{quiz_content}\n</details>\n"

    if run_manual and status_manual == 'failure':
        main_emoji = icons.get("failure", "❌")
        main_title = "Prerequisites Missing"
        is_failure = True
    elif run_plan and status_plan == 'failure':
        main_emoji = icons.get("warning", "⚠️")
        main_title = "Configuration Error"
        is_failure = True
    elif status_apply == 'failure':
        main_emoji = icons.get("failure", "❌")
        main_title = "Deployment Failed"
        is_failure = True

    rows_str = "\n".join(table_rows)
    table = f"""
| Step | Status | Info |
| :--- | :---: | :--- |
{rows_str}
"""

    report = f"""### {main_emoji} {config.get('course_name', 'Training Validation')}

**Task:** `{task_dir}`
**Result:** {main_title}

{table}
{extra_details}

<details><summary>Debug Info</summary>
Student: `{student_id}`
Checks: Quiz={run_quiz}, Manual={run_manual}, Plan={run_plan}
Event: {event_name}
</details>
"""

    with open("pr_comment.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    if is_failure:
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write("is_failure=true\n")

if __name__ == "__main__":
    main()