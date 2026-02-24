from dataclasses import dataclass

@dataclass
class Config:
    repo_path: str
    output_dir: str
    dependency_graph_dir: str
    # Остальные поля не нужны для анализатора, но могут требоваться для совместимости типов
    docs_dir: str = ""
    max_depth: int = 2
