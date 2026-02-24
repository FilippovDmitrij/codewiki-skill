import sys
import os
import json
import argparse
import re
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-file", required=True)
    args = parser.parse_args()

    with open(args.task_file, 'r') as f:
        content = f.read()

    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if not json_match:
        print("❌ Error: Invalid task format.")
        sys.exit(1)

    task_data = json.loads(json_match.group(1))

    # 1. Выводим ИНСТРУКЦИЮ (вшитый промпт)
    print("\n================================================================")
    print("🤖 AI INSTRUCTION (System Prompt)")
    print("================================================================")
    print(task_data.get("INSTRUCTION_TEMPLATE", "No instruction provided."))
    print("================================================================\n")

    # 2. Выводим КОНТЕКСТ

    # --- Логика для OVERVIEW ---
    if task_data.get("type") == "OVERVIEW":
        print("----------------------------------------------------------------")
        print("CONTEXT TYPE: SYSTEM OVERVIEW")
        print("TARGET FILE:  overview.md")
        print("----------------------------------------------------------------")

        dependencies = task_data.get("dependencies", [])
        docs_dir = Path(args.task_file).parent.parent / "docs"

        print("## PROJECT STRUCTURE (Top Level)\n")
        for dep in dependencies:
            print(f"- **{dep['name']}**: ./docs/{dep['doc_filename']}")

        print("\n## MODULE SUMMARIES (Context from Top-Level Docs)\n")

        for dep in dependencies:
            doc_path = docs_dir / dep['doc_filename']
            if doc_path.exists():
                print(f"\n### Module: {dep['name']}")
                print(f"(Content from {doc_path})\n")
                with open(doc_path, 'r', encoding='utf-8') as f:
                    print(f.read())
                print("-" * 40)
            else:
                print(f"⚠️  Warning: Documentation for {dep['name']} not found at {doc_path}")

        sys.exit(0)
    # ---------------------------

    target_components = task_data.get("components", [])
    children_modules = task_data.get("children_modules", [])
    module_name = task_data.get("module_name", "Unknown")
    module_full_name = task_data.get("module_full_name", module_name)
    module_path = task_data.get("module_path", "")

    # База данных
    base_dir = Path(args.task_file).parent.parent
    db_path = base_dir / "graph_raw.json"
    if not db_path.exists():
        db_path = Path("codewiki/graph_raw.json")

    db = {}
    if db_path.exists():
        with open(db_path, 'r') as f:
            db = json.load(f)

    context_type = task_data.get("type", "LEAF" if target_components else "CONTAINER")

    print("----------------------------------------------------------------")
    print(f"CONTEXT TYPE: {context_type}")
    print(f"MODULE ID:    {module_full_name}")
    print(f"TARGET FILE:  {module_full_name}.md  <-- YOU MUST USE THIS FILENAME")
    print("----------------------------------------------------------------")
    print(f"Path: {module_path}")
    print(f"Children count: {len(children_modules)}\n")

    if context_type == "MODULE":
        print("## SUB-MODULES (Children)")
        print("You must link to these existing documentation files:")
        print("| Logical Name | Link Target (Relative) |")
        print("| :--- | :--- |")
        for child in children_modules:
            name = child.get('logical_name') or child.get('short_name')
            link = child.get('doc_filename')
            print(f"| **{name}** | `./{link}` |")

        print("\n(Use the list above to generate the Architecture Overview and Links)")

    if context_type == "COMPONENT":
        print(f"## SOURCE CODE ({len(target_components)} items)")
        for cid in target_components:
            if cid in db:
                node = db[cid]
                print(f"\n### Component: {node['name']} ({node['component_type']})")
                print(f"File: {node['file_path']}")

                deps = node.get("depends_on", [])
                if deps:
                    print(f"Dependencies: {', '.join(deps[:10])}")

                print("```python")
                print(node.get('source_code', '# No source code'))
                print("```")
                print("-" * 40)

if __name__ == "__main__":
    main()
