import os
import json


class ReportWriter:
    def __init__(self, path):
        self.path = path

    def print_console(self, content):
        print(content)

    def save_json(self, filename, data):
        output_path = os.path.join(self.path, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def print_and_save(self, content, filename, data):
        self.print_console(content)
        self.save_json(filename, data)