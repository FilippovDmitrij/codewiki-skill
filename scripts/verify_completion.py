import sys
import os
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-file", required=True)
    parser.add_argument("--docs-dir", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.tree_file):
        print("❌ Module tree not found.")
        sys.exit(1)

    with open(args.tree_file, 'r') as f:
        module_tree = json.load(f)

    docs_dir = Path(args.docs_dir)
    missing_files = []
    
    # Та же логика генерации имени, что и в generate_tasks.py
    def get_expected_filename(path_parts):
        clean_parts = [p.replace("/", "_").replace(".", "_").lower() for p in path_parts if p]
        return "_".join(clean_parts) + ".md"

    def verify_node(node_name, node_data, path_stack):
        current_path_stack = path_stack + [node_name]
        
        # 1. Проверяем детей
        children = node_data.get("children", {})
        has_children_with_content = False
        
        if isinstance(children, dict):
            for child_name, child_data in children.items():
                child_has_content = verify_node(child_name, child_data, current_path_stack)
                if child_has_content:
                    has_children_with_content = True

        # 2. Проверяем текущий узел
        components = node_data.get("components", [])
        
        # Узел считается "существующим" для документации, если у него есть компоненты ИЛИ дети
        # (в generate_tasks.py используется та же логика: if current_components or children_full_names)
        should_exist = len(components) > 0 or has_children_with_content
        
        if should_exist:
            expected_name = get_expected_filename(current_path_stack)
            target_file = docs_dir / expected_name
            
            if not target_file.exists():
                missing_files.append(expected_name)
                # print(f"Missing: {expected_name}") # Debug
            
            return True # Этот узел должен был быть задокументирован
        
        return False

    print(f"🔍 Verifying documentation coverage in {docs_dir}...")
    
    for root_name, root_data in module_tree.items():
        verify_node(root_name, root_data, [])

    if missing_files:
        print(f"⚠️  Missing documentation for {len(missing_files)} modules:")
        for m in missing_files[:10]:
            print(f"   ❌ {m}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more.")
        
        # Важно вернуть ошибку, чтобы Claude понял, что надо работать дальше
        sys.exit(1)
    else:
        print("✅ All expected modules are documented.")
        sys.exit(0)

if __name__ == "__main__":
    main()