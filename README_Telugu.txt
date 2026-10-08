FASTAPI BANKING APPLICATION - STEP BY STEP

1. ZIP file extract cheyyandi.
2. Extract chesina folder ni VS Code lo Open Folder cheyyandi.
3. VS Code terminal open cheyyandi.
4. Virtual environment create cheyyandi:
   py -m venv venv
5. Activate cheyyandi (Windows PowerShell):
   .\venv\Scripts\Activate.ps1
   Execution policy error vaste, Command Prompt terminal open chesi:
   venv\Scripts\activate.bat
6. Packages install cheyyandi:
   pip install -r requirements.txt
7. Server run cheyyandi:
   uvicorn main:app --reload
8. Website:
   http://127.0.0.1:8000
9. FastAPI API docs:
   http://127.0.0.1:8000/docs

PROJECT FEATURES:
- Home page with banking service links
- New Account creation and database storage
- View Balance
- Deposit
- Withdraw (insufficient balance check)
- Transfer money to another account
- Close account (balance must be zero)
- Transaction history
- SQLite database file banking.db automatic ga create avuthundi.

TEST CHEYYADANIKI:
- First New Account lo account number (example: 1001), name, password, confirm password,
  initial amount, address, mobile number enter chesi create cheyyandi.
- Second account create cheyyandi (example: 1002) to test money transfer.
- Account number, name, password exact ga use cheyyandi.
- Transfer test: sender details + target account number + amount enter cheyyandi.

NOTE:
Idi learning/demo project. Real banking kosam security, authorization, audit, CSRF protection,
deployment, database backups, and regulatory requirements additional ga implement cheyyali.
