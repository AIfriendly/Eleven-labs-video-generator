
import subprocess
import sys
import os

python_exe = sys.executable
test_files = [
    "tests/processing/test_ffmpeg_resolution.py",
    "tests/cli/test_resolution_validation.py",
    "tests/ui/test_resolution_selector.py"
]

print(f"Running tests: {test_files}")

result = subprocess.run(
    [python_exe, "-m", "pytest"] + test_files + ["--tb=short", "-v"],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

with open("test_results.log", "w", encoding="utf-8") as f:
    f.write(f"Return code: {result.returncode}\n\n")
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(result.stderr)

print(f"Return code: {result.returncode}")
