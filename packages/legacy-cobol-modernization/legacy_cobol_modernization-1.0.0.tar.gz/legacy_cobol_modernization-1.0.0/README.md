# Modernizing  a Cobol accounting system to a Node.js application using GitHub Copilot

[![Unit Tests](https://github.com/mballot/modernize-legacy-cobol-app-epitech/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/mballot/modernize-legacy-cobol-app/actions/workflows/test.yml)
[![Golden Master Tests](https://img.shields.io/badge/Golden%20Master-Passing-brightgreen)](https://github.com/mballot/modernize-legacy-cobol-app/actions/workflows/test.yml)
[![Code Coverage](https://img.shields.io/badge/Coverage-80%2B%25-brightgreen)](https://github.com/mballot/modernize-legacy-cobol-app/actions/workflows/test.yml)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-PEP8-blue)](https://github.com/mballot/modernize-legacy-cobol-app/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/legacy-cobol-modernization)](https://pypi.org/project/legacy-cobol-modernization/)
[![PyPI downloads](https://img.shields.io/pypi/dm/legacy-cobol-modernization)](https://pypi.org/project/legacy-cobol-modernization/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![COBOL](https://img.shields.io/badge/COBOL-GnuCOBOL-orange)](https://gnucobol.sourceforge.io/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repo contains COBOL code for a simple accounting system. You can use GitHub Copilot to transform this code to a Node.js accounting system.

**Note: Keep in mind GitHub Copilot is an AI pair programmer that helps you write code. It is not a code generator and is using generative
models trained on public code. It may provide completions that are not perfect, safe, or otherwise suitable for production. Always review suggestions
and take a trust but verify approach.**

<img src="images/cobol_to_nodejs.png" alt="Cobol to Node.js" width="800"/>

## 📦 Quick Installation via PyPI

Install the modernized COBOL accounting system directly from PyPI:

```bash
# Install the package
pip install legacy-cobol-modernization

# Run the application
legacy-accounting
```

### Alternative Installation Methods

```bash
# Install with development tools
pip install legacy-cobol-modernization[dev]

# Install with testing tools only  
pip install legacy-cobol-modernization[test]

# Install from source
git clone https://github.com/mballot/modernize-legacy-cobol-app.git
cd modernize-legacy-cobol-app
pip install -e .
```

### Usage After Installation

```bash
# Run the accounting system
legacy-accounting

# Or use the alternative command
cobol-accounting
```

## Prerequisites

- Basic understanding of programming concepts.
- Basic understanding of the COBOL programming language.
- GitHub Copilot or GitHub Copilot Chat installed in your IDE or GitHub Codespace.

## Setup the development environment

### Option 1: Use an IDE that supports GitHub Copilot

- IDE options for both GitHub Copilot and Copilot Chat:
  - <img src="images/ide-vscode.png" alt="Visual Studio Code" width="20"/> Visual Studio Code
  - <img src="images/ide-vs.png" alt="Visual Studio" width="20"/> Visual Studio
  - <img src="images/ide-jetbrains.png" alt="JetBrains IDE" width="20"/> JetBrains IDE

#### For Visual Studio Code

- Install the GitHub Copilot and GitHub Copilot Chat extensions for Visual Studio Code.
- Install the COBOL extension for Visual Studio Code.

### Option 2: Use a GitHub codespace

- Create a new codespace in this repository. </br>
![Codespace](images/codespace.png)

- The configuration for the codespace is already set up with the required extensions.
  - GitHub Copilot
  - GitHub Copilot Chat
  - COBOL
  - Markdown All in One
  - Mermaid Markdown
  - python

## About the program

This COBOL program simulates an account management system. This program will involve multiple COBOL source files and perform various operations like crediting, debiting, viewing the balance, and even exiting the program. Here’s how you its structured:

- Main Program (main.cob): The main program will handle the user interface and call subprograms for different operations.
- Operations Program (operations.cob): This program will handle the actual operations like credit, debit, and view balance.
- Data Storage Program (data.cob): This program will manage the storage of the account balance.

## Steps to Compile and Run the Program

- Option 1: Install COBOL compiler on MaC
If you don't already have a COBOL compiler, you'll need to install one. Common COBOL compiler is GnuCOBOL: An open-source COBOL compiler. To Install , use brew:

```bash
brew install gnucobol 
```

- Option 2: Open the terminal in the GitHub codespace or Ubuntu Linux system and run the following command to install the COBOL compiler:

```bash
sudo apt-get update && \
sudo apt-get install gnucobol
```

reference: [gnucobol](https://formulae.brew.sh/formula/gnucobol)

- Compile, link and create executable: Link the object files together to create the final executable:

```bash
cobc -x main.cob operations.cob data.cob -o accountsystem
```

- Run the Program: Run the executable to start the account management system:

```bash
./accountsystem
```

## Program Interaction Example

- Program starts with user input menu

```bash
--------------------------------
Account Management System
1. View Balance
2. Credit Account
3. Debit Account
4. Exit
--------------------------------
Enter your choice (1-4): 
```

- User Chooses to View Balance:

```bash
Current balance: 1000.00
```

- User Chooses to Credit:

```bash
Enter credit amount:
200.00
Amount credited. New balance: 1200.00
```

- User Chooses to Debit:

```bash
Enter debit amount:
300.00
Amount debited. New balance: 900.00
```

- User Chooses to Exit:

```bash
Exiting the program. Goodbye!
```

## Explanation

- main.cob: This is the main interface where users select operations.
- operations.cob: It handles specific operations such as viewing, crediting, and debiting the account balance.
- data.cob: This program acts as a simple data storage, handling reading and writing of the balance.

This multi-file structure introduces modularity, making it easier to manage and extend the program. Each file has a clear responsibility, and the program flow is driven by user interaction.

### Data flow

```text
@workspace can you create a sequence diagram of the app showing the data flow of the app. Please create this in mermaid format so that I can render this in a markdown file.
```

```mermaid
sequenceDiagram
    participant User
    participant MainProgram
    participant Operations
    participant DataProgram

    User->>MainProgram: Start Application
    MainProgram->>User: Display Menu
    User->>MainProgram: Select Option (1-4)
    
    alt View Balance
        MainProgram->>Operations: CALL 'Operations' USING 'TOTAL'
        Operations->>DataProgram: CALL 'DataProgram' USING 'READ', FINAL-BALANCE
        DataProgram-->>Operations: RETURN FINAL-BALANCE
        Operations->>User: DISPLAY "Current balance: " FINAL-BALANCE
    end
    
    alt Credit Account
        MainProgram->>Operations: CALL 'Operations' USING 'CREDIT'
        Operations->>User: DISPLAY "Enter credit amount: "
        User->>Operations: Enter Amount
        Operations->>DataProgram: CALL 'DataProgram' USING 'READ', FINAL-BALANCE
        DataProgram-->>Operations: RETURN FINAL-BALANCE
        Operations->>Operations: ADD AMOUNT TO FINAL-BALANCE
        Operations->>DataProgram: CALL 'DataProgram' USING 'WRITE', FINAL-BALANCE
        DataProgram-->>Operations: RETURN
        Operations->>User: DISPLAY "Amount credited. New balance: " FINAL-BALANCE
    end
    
    alt Debit Account
        MainProgram->>Operations: CALL 'Operations' USING 'DEBIT'
        Operations->>User: DISPLAY "Enter debit amount: "
        User->>Operations: Enter Amount
        Operations->>DataProgram: CALL 'DataProgram' USING 'READ', FINAL-BALANCE
        DataProgram-->>Operations: RETURN FINAL-BALANCE
        alt Sufficient Funds
            Operations->>Operations: SUBTRACT AMOUNT FROM FINAL-BALANCE
            Operations->>DataProgram: CALL 'DataProgram' USING 'WRITE', FINAL-BALANCE
            DataProgram-->>Operations: RETURN
            Operations->>User: DISPLAY "Amount debited. New balance: " FINAL-BALANCE
        else Insufficient Funds
            Operations->>User: DISPLAY "Insufficient funds for this debit."
        end
    end
    
    alt Exit Application
        MainProgram->>MainProgram: MOVE 'NO' TO CONTINUE-FLAG
        MainProgram->>User: DISPLAY "Exiting the program. Goodbye!"
    end
```

## Generate a test plan

```text
@workspace The current Cobol app has no tests. Can you please create a test plan of current business logic that I can use to validate with business stakeholders about the current implementation.
Later I would like to use this test plan to create unit and integration tests in a node.js app. I am in the middle of transforming the current Cobol app to a node.js app.
The test plan should include the following:

1. Test Case ID
2. Test Case Description
3. Pre-conditions
4. Test Steps
5. Expected Result
6. Actual Result
7. Status (Pass/Fail)
8. Comments

Please create the test plan in a markdown table format. The test plan should cover all the business logic in the current Cobol app.
```

### Note

*You may still need follow up with another prompt to generate the markdown file format for the test plan.*

```markdown
Convert this to markdown syntax please to insert as a new file
```

## Convert files using prompt engineering best practices

### Create the Node.js project directory

```bash
mkdir node-accounting-app
cd node-accounting-app
```

### Use GitHub Copilot to convert the files iteratively

#### Convert main.cob to main.js

#### Convert operations.cob to operations.js

#### Convert data.cob to data.js

```text
Let's link all node.js files to work together in one accounting application, and then initialize, install dependencies, and run the application.
```

### Initialize a new Node.js project

```bash
npm init -y
```

### Install the Node.js app

```bash
npm install

```

### Run the Node.js app

```bash
node main.js
```

### Generate unit and integration tests

```text
@workspace I would like to create unit and integration tests cases form the test plan mentioned in
#file:TESTPLAN.md file The node.js code is in node-accounting-app folder and I am looking to generate tests
for #file:operations.js file. Use a popular testing framework and also provide all the dependencies required to run the tests.
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
