from pathlib import Path


def only_dirs(path: Path) -> bool:
    return all(p.is_dir() for p in path.iterdir())


def check_templates_static_structure(app, errors):
    """
    Id: 03
    Description : Verify that the `static/` and `templates/` folders contain only subfolders and no apps.

    Tags:
    - architecture

    Args:
        app (str or path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)
    app = app_path.name
    directories = ["templates", "static"]

    for dir_name in directories:
        dir_path = app_path / dir_name
        if not dir_path.exists():
            continue

        if not only_dirs(dir_path):
            errors.append(
                f"\n🚨 Structure incorrecte dans `{dir_name}` 🚨\n"
                f"Le dossier `{dir_name}` ne doit pas contenir des fichiers, il faut des sous-dossiers pour éviter des écrasements entre les applications django.\n\n"
            )
