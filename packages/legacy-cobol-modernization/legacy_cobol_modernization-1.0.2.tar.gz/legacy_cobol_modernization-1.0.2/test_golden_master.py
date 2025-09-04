import json
import subprocess


def run_python(inputs):
    process = subprocess.Popen(
        ["python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, _ = process.communicate("\n".join(inputs))
    return stdout


def load_golden_master():
    with open("golden_master.json") as f:
        return json.load(f)


# Generic function to create a test
def create_test_function(test_name, inputs, expected_output):
    def test_func():
        python_output = run_python(inputs)
        assert python_output.strip() == expected_output.strip(), (
            f"Test {test_name} failed"
        )

    return test_func


# Automatic test generation from golden master
golden_master = load_golden_master()

# Dynamic creation of tests for each scenario
for test_name, data in golden_master.items():
    test_func = create_test_function(test_name, data["inputs"], data["output"])
    # Assign test name for pytest
    test_func.__name__ = f"test_{test_name}"
    # Add test to global module
    globals()[f"test_{test_name}"] = test_func
