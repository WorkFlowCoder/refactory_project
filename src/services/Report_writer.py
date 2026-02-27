import os
import json
from typing import Any


class ReportWriter:
    def __init__(self, path: str):
        self.path = path

    def print_console(self, content: str) -> None:
        print(content)

    def save_json(self, filename: str, data: Any) -> None:
        output_path = os.path.join(self.path, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def print_and_save(self, content: str, filename: str, data: Any) -> None:
        self.print_console(content)
        self.save_json(filename, data)
