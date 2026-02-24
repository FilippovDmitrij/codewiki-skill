import sys
import os
import json
import logging
import argparse
from pathlib import Path

# Добавляем путь к src скилла, чтобы работали импорты
current_dir = Path(__file__).resolve().parent
skill_root = current_dir.parent
sys.path.insert(0, str(skill_root))

from src.dependency_analyzer.dependency_graphs_builder import DependencyGraphBuilder
from src.config import Config
from src.utils import file_manager

# Настройка логирования (только ошибки, чтобы не мусорить в stdout агента)
logging.basicConfig(level=logging.ERROR)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", required=True, help="Path to the repository to analyze")
    parser.add_argument("--output-dir", required=True, help="Path to save output JSONs")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    output_dir = os.path.abspath(args.output_dir)

    file_manager.ensure_directory(output_dir)

    # Создаем конфигурацию для анализатора
    config = Config(
        repo_path=repo_path,
        output_dir=output_dir,
        dependency_graph_dir=output_dir,
        docs_dir=os.path.join(output_dir, "docs")
    )

    print(f"🔍 Analyzing repository structure at: {repo_path}...")

    # Запускаем оригинальный билдер
    builder = DependencyGraphBuilder(config)
    # Эта функция парсит код и строит граф
    components, leaf_nodes = builder.build_dependency_graph()

    # 1. Формируем graph_raw.json (ПОЛНЫЙ дамп с исходным кодом)
    # Это нужно для скрипта get_context.py
    full_dump = {}
    for cid, node in components.items():
        node_dict = node.model_dump()
        # Конвертируем set в list для JSON сериализации
        if 'depends_on' in node_dict and isinstance(node_dict['depends_on'], set):
            node_dict['depends_on'] = list(node_dict['depends_on'])
        if 'depended_on_by' in node_dict and isinstance(node_dict['depended_on_by'], set):
            node_dict['depended_on_by'] = list(node_dict['depended_on_by'])
        full_dump[cid] = node_dict

    full_dump_path = os.path.join(output_dir, "graph_raw.json")
    file_manager.save_json(full_dump, full_dump_path)

    # 2. Формируем structure_summary.json (ОБЛЕГЧЕННЫЙ для LLM)
    # Убираем source_code, чтобы Claude мог прочитать весь файл и сделать кластеризацию
    summary_dump = []
    for cid, node in components.items():
        summary_dump.append({
            "id": cid,
            "name": node.name,
            "type": node.component_type,
            "file_path": node.relative_path,
            "dependencies": list(node.depends_on)
        })

    summary_path = os.path.join(output_dir, "structure_summary.json")
    file_manager.save_json(summary_dump, summary_path)

    print(f"✅ Analysis complete.")
    print(f"   Components found: {len(components)}")
    print(f"   Full data: {full_dump_path}")
    print(f"   Summary data: {summary_path}")

if __name__ == "__main__":
    main()
