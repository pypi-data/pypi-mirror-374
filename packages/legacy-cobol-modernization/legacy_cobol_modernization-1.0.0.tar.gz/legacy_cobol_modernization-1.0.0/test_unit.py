#!/usr/bin/env python3

import pytest

import main


class TestBusinessLogic:
    """Tests for business logic functions (without I/O)"""

    def setup_method(self):
        """Reset balance before each test"""
        main.reset_balance(1000.0)

    def test_get_balance(self):
        """Test balance retrieval"""
        assert main.get_balance() == 1000.0

        main.reset_balance(500.0)
        assert main.get_balance() == 500.0

    def test_reset_balance(self):
        """Test balance reset"""
        main.reset_balance(2500.0)
        assert main.get_balance() == 2500.0

        main.reset_balance()  # Default value
        assert main.get_balance() == 1000.0


class TestAmountProcessing:
    """Tests for amount processing according to COBOL rules"""

    def test_process_amount_valid_numbers(self):
        """Test with valid numbers"""
        assert main.process_amount_input("100") == 100.0
        assert main.process_amount_input("100.50") == 100.50
        assert main.process_amount_input("0") == 0.0
        assert main.process_amount_input("999999.99") == 999999.99

    def test_process_amount_negative_numbers(self):
        """Test with negative numbers (become positive)"""
        assert main.process_amount_input("-100") == 100.0
        assert main.process_amount_input("-50.25") == 50.25

    def test_process_amount_overflow(self):
        """Test with numbers too large (overflow -> 0)"""
        assert main.process_amount_input("1000000") == 0.0  # > 999999.99
        assert main.process_amount_input("10000000000000000000") == 0.0
        assert main.process_amount_input("999999.999") == 0.0  # > 999999.99

    def test_process_amount_invalid_input(self):
        """Test with invalid inputs (-> 0)"""
        assert main.process_amount_input("abc") == 0.0
        assert main.process_amount_input("") == 0.0
        assert main.process_amount_input("xyz123") == 0.0
        assert main.process_amount_input("12.34.56") == 0.0
        assert main.process_amount_input(None) == 0.0

    def test_process_amount_edge_cases(self):
        """Test edge cases"""
        assert main.process_amount_input("999999.98") == 999999.98
        assert main.process_amount_input("1000000.00") == 0.0
        assert main.process_amount_input("0.01") == 0.01


class TestMenuProcessing:
    """Tests for menu choice processing according to COBOL PIC 9 rules"""

    def test_process_menu_valid_choices(self):
        """Test with valid choices"""
        assert main.process_menu_choice("1") == 1
        assert main.process_menu_choice("2") == 2
        assert main.process_menu_choice("3") == 3
        assert main.process_menu_choice("4") == 4

    def test_process_menu_first_digit_only(self):
        """Test that only the first digit is taken (like COBOL PIC 9)"""
        assert main.process_menu_choice("100") == 1
        assert main.process_menu_choice("2000") == 2
        assert main.process_menu_choice("3.14") == 3
        assert main.process_menu_choice("4abc") == 4
        assert main.process_menu_choice("567") == 5

    def test_process_menu_invalid_choices(self):
        """Test with invalid choices (-> 0)"""
        assert main.process_menu_choice("abc") == 0
        assert main.process_menu_choice("") == 0
        assert main.process_menu_choice("xyz") == 0
        assert main.process_menu_choice(" ") == 0
        assert main.process_menu_choice(None) == 0

    def test_process_menu_edge_cases(self):
        """Test edge cases"""
        assert main.process_menu_choice("0") == 0
        assert main.process_menu_choice("9") == 9
        assert main.process_menu_choice(" 1 ") == 1  # With spaces
        assert main.process_menu_choice("1.0") == 1


class TestCreditOperation:
    """Tests for credit operations"""

    def setup_method(self):
        """Reset balance before each test"""
        main.reset_balance(1000.0)

    def test_credit_valid_amounts(self):
        """Test credit with valid amounts"""
        assert main.credit_operation("100")
        assert main.get_balance() == 1100.0

        assert main.credit_operation("50.25")
        assert main.get_balance() == 1150.25

    def test_credit_zero_amount(self):
        """Test credit with zero amount"""
        assert main.credit_operation("0")
        assert main.get_balance() == 1000.0  # No change

    def test_credit_negative_amount(self):
        """Test credit with negative amount (becomes positive)"""
        assert main.credit_operation("-100")
        assert main.get_balance() == 1100.0

    def test_credit_invalid_amount(self):
        """Test credit with invalid amount (treated as 0)"""
        assert main.credit_operation("abc")
        assert main.get_balance() == 1000.0  # No change

        assert main.credit_operation("")
        assert main.get_balance() == 1000.0  # No change

    def test_credit_overflow_amount(self):
        """Test credit with overflow amount (treated as 0)"""
        assert main.credit_operation("10000000000000000000")
        assert main.get_balance() == 1000.0  # No change

    def test_credit_max_valid_amount(self):
        """Test credit with maximum valid amount"""
        main.reset_balance(0.0)
        assert main.credit_operation("999999.99")
        assert main.get_balance() == 999999.99


class TestDebitOperation:
    """Tests for debit operations"""

    def setup_method(self):
        """Reset balance before each test"""
        main.reset_balance(1000.0)

    def test_debit_valid_amounts(self):
        """Test debit with valid amounts"""
        assert main.debit_operation("100")
        assert main.get_balance() == 900.0

        assert main.debit_operation("50.25")
        assert main.get_balance() == 849.75

    def test_debit_zero_amount(self):
        """Test debit with zero amount"""
        assert main.debit_operation("0")
        assert main.get_balance() == 1000.0  # No change

    def test_debit_negative_amount(self):
        """Test debit with negative amount (becomes positive)"""
        assert main.debit_operation("-100")
        assert main.get_balance() == 900.0

    def test_debit_insufficient_funds(self):
        """Test debit with insufficient funds"""
        assert not main.debit_operation("2000")
        assert main.get_balance() == 1000.0  # No change

        assert not main.debit_operation("1000.01")
        assert main.get_balance() == 1000.0  # No change

    def test_debit_exact_balance(self):
        """Test debit with exact balance amount"""
        assert main.debit_operation("1000")
        assert main.get_balance() == 0.0

    def test_debit_invalid_amount(self):
        """Test debit with invalid amount (treated as 0)"""
        assert main.debit_operation("abc")
        assert main.get_balance() == 1000.0  # No change

        assert main.debit_operation("")
        assert main.get_balance() == 1000.0  # No change

    def test_debit_overflow_amount(self):
        """Test debit with overflow amount (treated as 0)"""
        assert main.debit_operation("10000000000000000000")
        assert main.get_balance() == 1000.0  # No change


class TestCobolCompatibility:
    """Tests for COBOL behavior compatibility"""

    def setup_method(self):
        """Reset balance before each test"""
        main.reset_balance(1000.0)

    def test_cobol_pic_9_6_v_99_limits(self):
        """Test PIC 9(6)V99 limits"""
        # Values at the limit
        assert main.process_amount_input("999999.99") == 999999.99
        assert main.process_amount_input("999999.98") == 999999.98

        # Values that exceed the limit
        assert main.process_amount_input("1000000.00") == 0.0
        assert main.process_amount_input("999999.999") == 0.0

    def test_cobol_pic_9_menu_behavior(self):
        """Test PIC 9 behavior for menu choices"""
        # First digit only
        assert main.process_menu_choice("123") == 1
        assert main.process_menu_choice("456") == 4
        assert main.process_menu_choice("789") == 7

        # Non-numeric characters
        assert main.process_menu_choice("a1") == 0
        assert main.process_menu_choice("1a") == 1

    def test_multiple_operations_sequence(self):
        """Test a sequence of multiple operations"""
        # Credit then debit
        main.credit_operation("500")
        assert main.get_balance() == 1500.0

        main.debit_operation("200")
        assert main.get_balance() == 1300.0

        # Impossible debit
        result = main.debit_operation("2000")
        assert not result
        assert main.get_balance() == 1300.0  # No change

        # Credit with overflow (treated as 0)
        main.credit_operation("10000000000000000000")
        assert main.get_balance() == 1300.0  # No change


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=main", "--cov-report=term-missing"])
