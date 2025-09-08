import pytest
pytest.skip("Componentes Flet no disponibles", allow_module_level=True)

from smooth_criminal.flet_app.components import (
    function_table,
    action_buttons,
    info_panel
)
import flet as ft

def test_function_table_structure():
    table = function_table()
    assert isinstance(table, ft.DataTable)
    assert len(table.columns) == 5
    expected_headers = ["Function", "Decorator(s)", "Runs", "Avg Time (s)", "Score"]
    headers = [col.label.value for col in table.columns]
    assert headers == expected_headers

def test_action_buttons_creation():
    def dummy(*args): pass
    row = action_buttons(dummy, dummy, dummy, dummy)
    assert isinstance(row, ft.Row)
    assert len(row.controls) == 4
    labels = [btn.text for btn in row.controls]
    assert "Refresh" in labels[0]
    assert "Limpiar" in labels[1]
    assert "Exportar" in labels[2]
    assert "Gráfico" in labels[3]

def test_info_panel_display():
    panel = info_panel("Hola mundo", color="green")
    assert isinstance(panel, ft.Container)
    assert isinstance(panel.content, ft.Text)
    assert panel.content.value == "Hola mundo"
    assert panel.content.color == "green"
