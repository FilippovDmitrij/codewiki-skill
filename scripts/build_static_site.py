import sys
import os
import json
import argparse
import shutil
from pathlib import Path

current_dir = Path(__file__).resolve().parent
skill_root = current_dir.parent

def get_safe_full_name(path_parts):
    clean_parts = [p.replace("/", "_").replace(".", "_").lower() for p in path_parts if p]
    return "_".join(clean_parts)

def enrich_tree_with_filenames(node_dict, path_stack):
    for key, data in node_dict.items():
        current_stack = path_stack + [key]
        full_name = get_safe_full_name(current_stack)
        data['doc_filename'] = f"{full_name}.md"
        if 'children' in data and isinstance(data['children'], dict):
            enrich_tree_with_filenames(data['children'], current_stack)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", required=True)
    parser.add_argument("--tree-file", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    template_path = skill_root / "templates" / "github_pages" / "viewer_template.html"
    if not template_path.exists():
        print(f"❌ Template not found at {template_path}")
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()

    with open(args.tree_file, 'r') as f:
        module_tree = json.load(f)

    # Обогащаем дерево правильными именами файлов (с полным путём-стеком)
    enrich_tree_with_filenames(module_tree, [])
    module_tree_json = json.dumps(module_tree)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📦 Copying markdown files to html output...")
    docs_source = Path(args.docs_dir)
    if docs_source.exists():
        for md_file in docs_source.glob("*.md"):
            shutil.copy(md_file, output_dir)
    else:
        print(f"⚠️ Warning: Docs dir {docs_source} does not exist.")

    print("🎨 Generating index.html...")

    html_content = template_str.replace("{{TITLE}}", "Codebase Documentation")
    html_content = html_content.replace("{{REPO_LINK}}", "")
    html_content = html_content.replace("{{SHOW_INFO}}", "none")
    html_content = html_content.replace("{{INFO_CONTENT}}", "")
    html_content = html_content.replace("{{CONFIG_JSON}}", "{}")
    html_content = html_content.replace("{{METADATA_JSON}}", "{}")
    html_content = html_content.replace("{{MODULE_TREE_JSON}}", module_tree_json)
    html_content = html_content.replace("{{DOCS_BASE_PATH}}", ".")

    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Static site generated at: {output_dir}/index.html")

if __name__ == "__main__":
    main()
