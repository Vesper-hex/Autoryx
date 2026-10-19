import pytest
from app.services.validation.repair_service import RepairService

def test_repair_service_zero_repairs_when_passing():
    code = """#include <iostream>
int main() {
    int x;
    if (std::cin >> x) std::cout << (x + 1) << "\\n";
    return 0;
}
"""
    result = RepairService.validate_and_repair(
        initial_code=code,
        filename="test.cpp",
        language="cpp",
        question_description="Add 1 to the input integer",
        sample_inputs=["5"],
        sample_outputs=["6"],
        max_repairs=2,
        provider_name="mock"
    )
    assert result["validation_status"] == "passed"
    assert result["repair_attempts"] == 0
    assert len(result["repair_history"]) == 0

def test_repair_service_bounded_attempts():
    # Broken code with missing semicolon
    broken_code = """#include <iostream>
int main() {
    int a = 5
    std::cout << a << std::endl;
    return 0;
}
"""
    result = RepairService.validate_and_repair(
        initial_code=broken_code,
        filename="test.cpp",
        language="cpp",
        question_description="Print 5",
        sample_inputs=[""],
        sample_outputs=["5"],
        max_repairs=2,
        provider_name="mock"
    )
    # The mock repair provider fixes the missing semicolon!
    assert result["repair_attempts"] <= 2
    assert len(result["repair_history"]) > 0
    assert result["validation_status"] == "passed"
