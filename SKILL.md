---
name: codewiki-orchestrator
description: Transform codebase into comprehensive documentation using a multi-agent approach. Orchestrate analysis, architecture planning, and writing tasks.
version: 1.0.0
---

# CodeWiki Orchestration

You are the **Project Manager** responsible for documenting this codebase. Your goal is to orchestrate the process using `uv` for all Python operations and Sub-Agents for cognitive tasks.

## 🐍 Python Environment Rules (CRITICAL)
**CRITICAL:** This project uses UV for all Python operations to ensure isolation and reproducibility.
1.  **NEVER** use `python -m`, `pip install`, or `python script.py` directly.
2.  **ALWAYS** work from the skill directory and use:
    *   `uv pip install -r requirements.txt` for setup
    *   `uv run python scripts/...` for script execution

## 🚀 Workflow

**IMPORTANT:** Always run from codewiki-skill directory

### Phase 0: Setup
Initialize dependencies before doing anything else.
```bash
uv venv && uv pip install -r requirements.txt
```

### Phase 1: Analysis (Main Agent)
Run the analyzer to parse the codebase and extract raw metadata.
```bash
uv run python scripts/analyze_dependencies.py --repo-path ../.. --output-dir ../../codewiki
```
*Result:* `codewiki/structure_summary.json` (for Architects) and `graph_raw.json` (for Writers) are created.

### Phase 2: Architecture (Delegate to Sub-Agent)
**DO NOT** do this yourself. Assign a **Sub-Agent** (Role: Architect) to create the module tree.

**Instruction for Sub-Agent: - when you assign tasks to Sub-Agents, you must provide FULL PATHS**
1.  **Read Prompt:** Read `{path}/prompts/structuring-modules.md`.
2.  **Read Data:** Read `{path}/codewiki/structure_summary.json`. Analyze the file structure and dependencies. Group them into logical modules (clustering). Create a hierarchical JSON.
3.  **Execute:** Create the `{path}/codewiki/module_tree.json` following the schema in the prompt.

### Phase 3: Task Generation (Main Agent)
Convert the architecture plan into actionable tasks.
```bash
uv run python scripts/generate_tasks.py \
    --tree-path ../../codewiki/module_tree.json \
    --output-dir ../../codewiki/tasks \
    --templates-dir prompts
```
*Result:* A list of markdown task files (e.g., `tasks/001_task_auth.md`).

### Phase 4: Execution Loop (Delegate to Writer Sub-Agents)
**YOUR PRIMARY JOB:** Orchestrate parallel execution. The tasks are generated in **Bottom-Up Order** (numbered). The last task (`9999_task_repository_overview.md`) is always the Overview and must run **after all others**.

1.  Take the list of tasks from Phase 3 `../../codewiki/tasks/`. Sort by name/number. Process all tasks **except** `9999_task_repository_overview.md` first.
2.  **Sequential Batch Processing:** Assign next tasks to **Sub-Agents** (only 3 tasks per batch).
3.  **Instruction for Writer Sub-Agent - when you assign tasks to Sub-Agents, you must provide FULL PATHS**
    > 1. Read your assigned task file: `{path_to_task_md}`.
    > 2. **Run Context Fetcher:** Execute `uv run python {path}/scripts/fetch_context.py --task-file {task_file_path}`.
    > 3. **Perform Task:** The output of the previous command contains two sections:
    >    - **AI INSTRUCTION:** The specific prompt template telling you exactly how to write this document.
    >    - **CONTEXT:** The source code or child module summaries you need.
    > 4. **Action:** Follow the "AI INSTRUCTION" using the "CONTEXT" to generate the documentation file at `{path}/codewiki/docs/{module_full_name}.md`.
    > 5. Report only 'Done' when finished.

4.  **Monitor:** Wait for Sub-Agents to confirm completion before taking the next batch (to ensure dependencies are documented first).
5.  **Final Step:** After all normal tasks are done, assign `9999_task_repository_overview.md` to a Sub-Agent as the last task.

### Phase 5: Verification (Main Agent)
Check if any modules were missed.
```bash
uv run python scripts/verify_completion.py \
    --tree-file ../../codewiki/module_tree.json \
    --docs-dir ../../codewiki/docs
```
*   **If missing files:** The script returns a list of missing modules. Go back to **Phase 3** (generate tasks only for missing modules) -> **Phase 4**.
*   **If success:** Proceed to Phase 6.

### Phase 6: Finalization (Main Agent)
Generate the static HTML site.
```bash
uv run python scripts/build_static_site.py \
    --docs-dir ../../codewiki/docs \
    --tree-file ../../codewiki/module_tree.json \
    --output-dir ../../codewiki/html
```
