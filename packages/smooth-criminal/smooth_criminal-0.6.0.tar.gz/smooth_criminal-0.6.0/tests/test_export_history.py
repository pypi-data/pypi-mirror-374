import os
import json
import csv
from pathlib import Path

import openpyxl

from smooth_criminal.core import auto_boost
from smooth_criminal.memory import export_execution_history, LOG_PATH

@auto_boost()
def export_test_func():
    return sum(i for i in range(1000))

def test_export_to_multiple_formats(tmp_path):
    # Ejecutar función varias veces para llenar historial
    for _ in range(2):
        export_test_func()

    # Rutas de exportación temporales
    csv_path = tmp_path / "export.csv"
    json_path = tmp_path / "export.json"
    xlsx_path = tmp_path / "export.xlsx"
    md_path = tmp_path / "export.md"

    # Exportar a CSV
    result_csv = export_execution_history(csv_path, format="csv")
    assert result_csv
    assert csv_path.exists()

    # Comprobar contenido del CSV
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) >= 1
        assert "function" in rows[0]
        assert rows[0]["function"] == "export_test_func"

    # Exportar a JSON
    result_json = export_execution_history(json_path, format="json")
    assert result_json
    assert json_path.exists()

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert any(entry["function"] == "export_test_func" for entry in data)

    # Exportar a XLSX
    result_xlsx = export_execution_history(xlsx_path, format="xlsx")
    assert result_xlsx
    assert xlsx_path.exists()
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    assert rows[0][0] == "function"
    assert any(r[0] == "export_test_func" for r in rows[1:])

    # Exportar a Markdown
    result_md = export_execution_history(md_path, format="md")
    assert result_md
    assert md_path.exists()
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
        assert "export_test_func" in content
        assert content.startswith("| function |")
