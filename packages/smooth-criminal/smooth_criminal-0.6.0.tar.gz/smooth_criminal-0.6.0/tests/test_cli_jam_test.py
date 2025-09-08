import subprocess
import sys
import json
from pathlib import Path


def test_jam_test_cli_output():
    repo_root = Path(__file__).resolve().parent.parent
    cmd = [
        sys.executable,
        "-m",
        "smooth_criminal.cli",
        "jam-test",
        "tests.sample_funcs:compute",
        "--workers",
        "2",
        "--reps",
        "1",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    output = result.stdout + result.stderr
    assert "thread" in output
    assert "process" in output
    assert "async" in output
    assert result.returncode == 0


def test_jam_test_cli_silent_json():
    repo_root = Path(__file__).resolve().parent.parent
    cmd = [
        sys.executable,
        "-m",
        "smooth_criminal.cli",
        "jam-test",
        "tests.sample_funcs:compute",
        "--workers",
        "2",
        "--reps",
        "1",
        "--silent",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    assert result.stderr == ""
    data = json.loads(result.stdout)
    assert set(data["averages"].keys()) == {"thread", "process", "async"}
    assert result.returncode == 0


def test_jam_test_cli_message_non_silent():
    repo_root = Path(__file__).resolve().parent.parent
    cmd = [
        sys.executable,
        "-m",
        "smooth_criminal.cli",
        "jam-test",
        "tests.sample_funcs:compute",
        "--workers",
        "2",
        "--reps",
        "1",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    output = result.stdout + result.stderr
    assert "🎶 Just jammin' through those CPU cores! 🧠🕺" in output
    assert result.returncode == 0

