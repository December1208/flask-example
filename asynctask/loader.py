import pathlib
from typing import List


class TaskDirsLoader:

    def __init__(self, base_path, task_dir_name: str) -> None:
        self.base_path = pathlib.Path(base_path)
        self.task_dir_name = task_dir_name

    def generate_task_dirs(self):
        if not self.base_path.exists():
            return []
        task_dirs = []
        for dir_path in self.base_path.iterdir():
            if dir_path.is_file():
                continue

            task_path = dir_path / self.task_dir_name
            if not task_path.exists() or task_path.is_file():
                continue
            task_dirs.append(task_path)
        return task_dirs


class AsyncTaskLoader:

    def __init__(self, task_base_dirs: List[TaskDirsLoader], base_dir):
        self.task_base_dirs = task_base_dirs
        self.base_dir = base_dir

    def generate_load_path(self) -> List[str]:
        task_dirs = []
        for task_basedir in self.task_base_dirs:
            task_dirs.extend(task_basedir.generate_task_dirs())

        task_module_paths = []
        for task_basedir in task_dirs:
            sub_task_module_paths = self.load_tasks_from(
                self.base_dir, task_basedir
            )
            task_module_paths.extend(sub_task_module_paths)
        return task_module_paths

    def load_tasks_from(self, base_dir: pathlib.Path, task_dir: pathlib.Path):
        includes = []
        full_task_dir = base_dir / task_dir
        for file in full_task_dir.glob("*.pyc"):
            file_path = str(file).split('.')[0].replace('/', '.')
            includes.append(file_path)
        for file in full_task_dir.glob("*.py"):
            file_path = str(file).split('.')[0].replace('/', '.')
            includes.append(file_path)
        return includes
