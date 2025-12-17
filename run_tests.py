import subprocess
import sys
import os

# Use the same Python interpreter that's running this script
python_exe = sys.executable
print(f"Using Python: {python_exe}")

# Run pytest
result = subprocess.run(
    [python_exe, "-m", "pytest", "tests/ui/test_progress.py", "--tb=short", "-v"],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

# Write results to file
with open("test_results.log", "w", encoding="utf-8") as f:
    f.write(f"Python: {python_exe}\n")
    f.write(f"CWD: {os.getcwd()}\n\n")
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(result.stderr)
    f.write(f"\n\nReturn code: {result.returncode}")

print(f"Return code: {result.returncode}")
print("Results written to test_results.log")
