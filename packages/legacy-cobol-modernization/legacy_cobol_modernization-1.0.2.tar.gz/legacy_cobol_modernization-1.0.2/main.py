#!/usr/bin/env python3

# Balance file for persistence
BALANCE_FILE = "balance.json"

# Global variables (like in COBOL)
balance = 1000.00

# === BUSINESS LOGIC FUNCTIONS (without I/O) ===


def get_balance():
    """Returns the current balance"""
    return balance


def process_amount_input(input_value):
    """
    Processes user input as COBOL PIC 9(6)V99 would do
    Returns the processed amount according to COBOL rules
    """
    try:
        amount = abs(float(input_value))
        # COBOL limit: PIC 9(6)V99 = maximum 999999.99
        max_cobol_value = 999999.99

        # In COBOL, if the number exceeds the limit, it is treated as 0
        if amount > max_cobol_value:
            return 0.0
        return amount
    except (ValueError, TypeError):
        # In COBOL, non-numeric characters are treated as 0
        return 0.0


def process_menu_choice(input_value):
    """
    Processes a menu choice as COBOL PIC 9 would do
    Returns the first digit or 0 if invalid
    """
    try:
        input_str = str(input_value).strip()
        if input_str and input_str[0].isdigit():
            # Like in COBOL PIC 9, we only keep the first digit
            return int(input_str[0])
        return 0
    except (ValueError, IndexError, AttributeError):
        return 0


def credit_operation(amount):
    """
    Performs a credit operation
    Returns True if the operation succeeded, False otherwise
    """
    global balance
    processed_amount = process_amount_input(amount)
    balance += processed_amount
    return True


def debit_operation(amount):
    """
    Performs a debit operation
    Returns True if the operation succeeded, False if insufficient funds
    """
    global balance
    processed_amount = process_amount_input(amount)

    if balance >= processed_amount:
        balance -= processed_amount
        return True
    return False


def reset_balance(new_balance=1000.0):
    """Resets the balance to a given value (for testing)"""
    global balance
    balance = new_balance


# === USER INTERFACE FUNCTIONS ===


def view_balance():
    """Displays the current balance"""
    print(f"Current balance: {balance:09.2f}")


def credit_account():
    """Interface for crediting an account"""
    print("Enter credit amount: ")
    amount_input = input()
    credit_operation(amount_input)
    print(f"Amount credited. New balance: {balance:09.2f}")


def debit_account():
    """Interface for debiting an account"""
    print("Enter debit amount: ")
    amount_input = input()

    if debit_operation(amount_input):
        print(f"Amount debited. New balance: {balance:09.2f}")
    else:
        print("Insufficient funds for this debit.")


def main():
    """Main function with menu loop"""
    continue_flag = "YES"

    while continue_flag != "NO":
        print("--------------------------------")
        print("Account Management System")
        print("1. View Balance")
        print("2. Credit Account")
        print("3. Debit Account")
        print("4. Exit")
        print("--------------------------------")
        print("Enter your choice (1-4): ", end="\n")

        user_input = input().strip()
        user_choice = process_menu_choice(user_input)

        if user_choice == 1:
            view_balance()
        elif user_choice == 2:
            credit_account()
        elif user_choice == 3:
            debit_account()
        elif user_choice == 4:
            continue_flag = "NO"
        else:
            print("Invalid choice, please select 1-4.")

    print("Exiting the program. Goodbye!")


if __name__ == "__main__":
    main()
