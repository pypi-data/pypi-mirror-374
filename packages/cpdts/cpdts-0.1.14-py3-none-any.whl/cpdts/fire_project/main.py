
import os
from pathlib import Path
from ..utils import create_file_with_path



def fire_create(project_name):
    # 获取当前模块文件的目录
    current_dir = Path(__file__).parent

    items = {
        ".vscode/settings.json":{
            "template": "/templates/vscode/settings.json",
        },
        ".kiro/hooks/auto-init-imports.kiro.hook":{
            "template": "/templates/kiro/auto-init-imports.kiro.hook",
        },
        ".kiro/hooks/build-publish-package.kiro.hook":{
            "template": "/templates/kiro/build-publish-package.kiro.hook",
        },
        ".kiro/steering/main.md":{
            "template": "/templates/kiro/main.md",
        },
        f"src/{project_name}/__init__.py":{
            "template": "templates/src/init.py",
        },
        f"src/{project_name}/scripts/clean_dist.py":{
            "template": "templates/scripts/clean_dist.py",
        },
        "pyproject.toml":{
            "template": "templates/pyproject.toml.j2",
            "data": {
                "project_name": project_name
            }
        },
        ".gitignore":{
            "template": "templates/.gitignore",
        },
        "README.md":{
            "template": "templates/README.md",
        }
    }


    for item in items:
        template = items[item]["template"]
        data = items[item].get("data", {})
        create_file_with_path(f'{project_name}/{item}', f"{current_dir}/{template}", data)


    # create_file_with_path(f'{project_name}/.vscode/settings.json', f"{current_dir}/templates/vscode/settings.json")

    pass


