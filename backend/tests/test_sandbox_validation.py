import pytest
from app.services.validation.compilers.cpp_compiler import CppCompiler
from app.services.validation.compilers.java_compiler import JavaCompiler
from app.services.validation.compilers.python_runner import PythonRunner

def test_cpp_compilation_and_test_pass():
    code = """#include <iostream>
int main() {
    int a, b;
    if (std::cin >> a >> b) {
        std::cout << (a + b) << "\\n";
    }
    return 0;
}
"""
    result = CppCompiler.validate(
        source_code=code,
        filename="solution.cpp",
        sample_inputs=["10 20", "5 7"],
        sample_outputs=["30", "12"]
    )
    assert result["compilation_status"] == "passed"
    assert result["validation_status"] == "passed"
    assert result["tests_total"] == 2
    assert result["tests_passed"] == 2

def test_cpp_compilation_failure_handling():
    invalid_code = """#include <iostream>
int main() {
    this_is_an_invalid_syntax_error!
    return 0;
}
"""
    result = CppCompiler.validate(
        source_code=invalid_code,
        filename="bad.cpp",
        sample_inputs=["1 2"],
        sample_outputs=["3"]
    )
    assert result["compilation_status"] == "failed"
    assert result["validation_status"] == "failed"
    assert "error" in result["compiler_output"].lower()

def test_python_runner_pass():
    py_code = """import sys
tokens = sys.stdin.read().split()
if len(tokens) >= 2:
    print(int(tokens[0]) * int(tokens[1]))
"""
    result = PythonRunner.validate(
        source_code=py_code,
        filename="solution.py",
        sample_inputs=["4 5", "3 7"],
        sample_outputs=["20", "21"]
    )
    assert result["compilation_status"] == "passed"
    assert result["validation_status"] == "passed"
    assert result["tests_passed"] == 2

def test_java_compilation_and_run():
    java_code = """import java.util.Scanner;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            System.out.println(n * 2);
        }
    }
}
"""
    result = JavaCompiler.validate(
        source_code=java_code,
        filename="Solution.java",
        sample_inputs=["15", "8"],
        sample_outputs=["30", "16"]
    )
    assert result["compilation_status"] == "passed"
    assert result["validation_status"] == "passed"
    assert result["tests_passed"] == 2
