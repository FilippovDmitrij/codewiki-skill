import sys
import os
import json
import argparse
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-path", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--templates-dir", default="prompts")
    args = parser.parse_args()

    if not os.path.exists(args.tree_path):
        print(f"❌ Error: {args.tree_path} not found.")
        sys.exit(1)

    # 1. Загружаем шаблоны в память
    templates_dir = Path(args.templates_dir)
    try:
        tpl_component = (templates_dir / "component.md").read_text(encoding='utf-8')
        tpl_module = (templates_dir / "module.md").read_text(encoding='utf-8')
        tpl_system = (templates_dir / "system.md").read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error loading templates from '{templates_dir}': {e}")
        sys.exit(1)

    with open(args.tree_path, 'r') as f:
        module_tree = json.load(f)

    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.makedirs(args.output_dir, exist_ok=True)

    tasks_created = []
    task_counter = 0

    def get_safe_full_name(path_parts):
        clean_parts = [p.replace("/", "_").replace(".", "_").lower() for p in path_parts if p]
        return "_".join(clean_parts)

    def process_node(node_name, node_data, path_stack):
        nonlocal task_counter
        current_path_stack = path_stack + [node_name]

        # 1. Рекурсия: сначала дети
        children = node_data.get("children", {})
        children_doc_info = []

        if isinstance(children, dict):
            for child_name, child_data in children.items():
                child_full_name = process_node(child_name, child_data, current_path_stack)
                if child_full_name:
                    children_doc_info.append({
                        "logical_name": child_name,
                        "doc_filename": f"{child_full_name}.md"
                    })

        # 2. Обработка текущего узла
        current_components = node_data.get("components", [])

        if current_components or children_doc_info:
            task_counter += 1
            full_module_name = get_safe_full_name(current_path_stack)

            # Определяем тип и подбираем шаблон
            if current_components:
                task_type = "COMPONENT"
                instruction = tpl_component
            else:
                task_type = "MODULE"
                instruction = tpl_module.replace("{module_name}", node_name)

            task_filename = f"{task_counter:04d}_task_{full_module_name}.md"
            task_path = os.path.join(args.output_dir, task_filename)

            task_content = {
                "task_id": task_counter,
                "type": task_type,
                "module_name": node_name,
                "module_full_name": full_module_name,
                "module_path": node_data.get("path", ""),
                "components": current_components,
                "children_modules": children_doc_info,
                "INSTRUCTION_TEMPLATE": instruction
            }

            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(f"# Task: Document {node_name}\n\n```json\n")
                json.dump(task_content, f, indent=2, ensure_ascii=False)
                f.write("\n```\n")

            tasks_created.append(task_path)
            return full_module_name

        return None

    for root_name, root_data in module_tree.items():
        process_node(root_name, root_data, [])

    # --- Генерация финального Overview ---
    print("🌟 Generating Final Overview Task...")

    top_level_modules = []
    for root_name in module_tree.keys():
        safe_name = root_name.replace("/", "_").replace(".", "_").lower()
        top_level_modules.append({"name": root_name, "doc_filename": f"{safe_name}.md"})

    task_counter += 1
    overview_content = {
        "task_id": task_counter,
        "type": "OVERVIEW",
        "module_name": "Repository Overview",
        "module_full_name": "overview",
        "target_file": "overview.md",
        "dependencies": top_level_modules,
        "INSTRUCTION_TEMPLATE": tpl_system
    }

    overview_path = os.path.join(args.output_dir, "9999_task_repository_overview.md")
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write("# Task: System Overview\n\n```json\n")
        json.dump(overview_content, f, indent=2, ensure_ascii=False)
        f.write("\n```\n")

    tasks_created.append(overview_path)

    print(f"✅ Generated {len(tasks_created)} tasks with embedded templates in {args.output_dir}")

if __name__ == "__main__":
    main()
