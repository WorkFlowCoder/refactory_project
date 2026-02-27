"""import os
import json
import tempfile
from services.report_writer import ReportWriter

def test_print_and_save():
    content = "Hello World"
    data = {"key": "value"}

    with tempfile.TemporaryDirectory() as tmpdir:
        writer = ReportWriter(tmpdir)
        filename = "test.json"

        # Appel de la méthode
        writer.write(content, filename, data)

        # Vérifier que le fichier a été créé
        file_path = os.path.join(tmpdir, filename)
        assert os.path.exists(file_path)

        # Vérifier le contenu du JSON
        with open(file_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data"""
