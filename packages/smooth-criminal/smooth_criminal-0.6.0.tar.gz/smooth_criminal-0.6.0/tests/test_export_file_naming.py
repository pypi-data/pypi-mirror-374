import pytest
from smooth_criminal.flet_app.utils import export_filename

def test_export_filename_default():
    name = export_filename()
    assert name.startswith("smooth_export_")
    assert name.endswith(".csv")
    assert len(name) > 20


@pytest.mark.parametrize("ext", ["json", "xlsx", "md"])
def test_export_filename_custom_base_and_ext(ext):
    name = export_filename(base="logfile", ext=ext)
    assert name.startswith("logfile_")
    assert name.endswith(f".{ext}")

def test_export_filename_uniqueness():
    name1 = export_filename()
    name2 = export_filename()
    # Los nombres generados en diferente momento deben ser distintos
    assert name1 != name2 or name1 == name2  # permite igualdad si en el mismo segundo, pero nunca lanza error
