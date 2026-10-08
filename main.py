from decimal import Decimal, InvalidOperation
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models import Account, Transaction
from security import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SDFC Bank - Banking Application")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def money(value):
    return f"{Decimal(str(value or 0)):.2f}"


templates.env.filters["money"] = money


def render_page(request: Request, page: str, message: str = "", message_type: str = "success", **context):
    return templates.TemplateResponse(
        request=request,
        name=page,
        context={"request": request, "message": message, "message_type": message_type, **context},
    )


def get_valid_account(db: Session, account_number: str, name: str, password: str):
    account = db.query(Account).filter(Account.account_number == account_number.strip()).first()
    if not account:
        return None
    if account.name.strip().casefold() != name.strip().casefold():
        return None
    if not verify_password(password, account.password_hash):
        return None
    return account


def parse_amount(value: str):
    try:
        amount = Decimal(value).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return None
    if not amount.is_finite() or amount <= 0:
        return None
    return amount


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_page(request, "home.html")


@app.get("/new-account", response_class=HTMLResponse)
def new_account_page(request: Request):
    return render_page(request, "new_account.html")


@app.post("/new-account", response_class=HTMLResponse)
def create_account(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    amount: str = Form(...),
    address: str = Form(...),
    mobile_no: str = Form(...),
    db: Session = Depends(get_db),
):
    account_number = account_number.strip()
    name = name.strip()
    address = address.strip()
    mobile_no = mobile_no.strip()

    if not all([account_number, name, password, address, mobile_no]):
        return render_page(request, "new_account.html", "Please fill in every field.", "error")
    if password != confirm_password:
        return render_page(request, "new_account.html", "Password and confirm password do not match.", "error")
    initial_amount = parse_amount(amount)
    if initial_amount is None and amount.strip() not in ("0", "0.0", "0.00"):
        return render_page(request, "new_account.html", "Enter a valid amount (zero or a positive amount).", "error")
    if initial_amount is None:
        try:
            initial_amount = Decimal(amount).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return render_page(request, "new_account.html", "Enter a valid initial amount.", "error")
    if initial_amount < 0:
        return render_page(request, "new_account.html", "Initial amount cannot be negative.", "error")

    account = Account(
        account_number=account_number,
        name=name,
        password_hash=hash_password(password),
        balance=initial_amount,
        address=address,
        mobile_no=mobile_no,
    )
    db.add(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_page(request, "new_account.html", "That account number already exists. Please use another one.", "error")

    if initial_amount > 0:
        db.add(Transaction(
            account_number=account_number,
            transaction_type="Opening Deposit",
            amount=initial_amount,
            description="Initial account balance",
        ))
        db.commit()

    return render_page(
        request,
        "result.html",
        f"Account created successfully. Your account number is {account_number}.",
        "success",
        title="Account Created",
    )


@app.get("/balance", response_class=HTMLResponse)
def balance_page(request: Request):
    return render_page(request, "balance.html")


@app.post("/balance", response_class=HTMLResponse)
def check_balance(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_valid_account(db, account_number, name, password)
    if not account:
        return render_page(request, "balance.html", "Invalid account number, name, or password.", "error")
    return render_page(request, "result.html", "Account details verified.", "success",
                       title="View Balance", account=account)


@app.get("/deposit", response_class=HTMLResponse)
def deposit_page(request: Request):
    return render_page(request, "deposit.html")


@app.post("/deposit", response_class=HTMLResponse)
def deposit_money(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    amount: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_valid_account(db, account_number, name, password)
    if not account:
        return render_page(request, "deposit.html", "Invalid account number, name, or password.", "error")
    value = parse_amount(amount)
    if value is None:
        return render_page(request, "deposit.html", "Enter a deposit amount greater than zero.", "error")
    account.balance = Decimal(str(account.balance)) + value
    db.add(Transaction(account_number=account.account_number, transaction_type="Deposit",
                       amount=value, description="Cash deposit"))
    db.commit()
    db.refresh(account)
    return render_page(request, "result.html", f"Deposit of ₹{value:.2f} completed successfully.",
                       "success", title="Deposit Successful", account=account)


@app.get("/withdraw", response_class=HTMLResponse)
def withdraw_page(request: Request):
    return render_page(request, "withdraw.html")


@app.post("/withdraw", response_class=HTMLResponse)
def withdraw_money(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    amount: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_valid_account(db, account_number, name, password)
    if not account:
        return render_page(request, "withdraw.html", "Invalid account number, name, or password.", "error")
    value = parse_amount(amount)
    if value is None:
        return render_page(request, "withdraw.html", "Enter a withdrawal amount greater than zero.", "error")
    current_balance = Decimal(str(account.balance))
    if value > current_balance:
        return render_page(request, "withdraw.html", "Insufficient balance. Withdrawal was not completed.", "error")
    account.balance = current_balance - value
    db.add(Transaction(account_number=account.account_number, transaction_type="Withdraw",
                       amount=value, description="Cash withdrawal"))
    db.commit()
    db.refresh(account)
    return render_page(request, "result.html", f"Withdrawal of ₹{value:.2f} completed successfully.",
                       "success", title="Withdrawal Successful", account=account)


@app.get("/transfer", response_class=HTMLResponse)
def transfer_page(request: Request):
    return render_page(request, "transfer.html")


@app.post("/transfer", response_class=HTMLResponse)
def transfer_money(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    target_account: str = Form(...),
    amount: str = Form(...),
    db: Session = Depends(get_db),
):
    sender = get_valid_account(db, account_number, name, password)
    if not sender:
        return render_page(request, "transfer.html", "Invalid sender account number, name, or password.", "error")
    target_account = target_account.strip()
    receiver = db.query(Account).filter(Account.account_number == target_account).first()
    if not receiver:
        return render_page(request, "transfer.html", "Target account was not found.", "error")
    if receiver.account_number == sender.account_number:
        return render_page(request, "transfer.html", "You cannot transfer money to the same account.", "error")
    value = parse_amount(amount)
    if value is None:
        return render_page(request, "transfer.html", "Enter a transfer amount greater than zero.", "error")
    sender_balance = Decimal(str(sender.balance))
    if value > sender_balance:
        return render_page(request, "transfer.html", "Insufficient balance. Transfer was not completed.", "error")

    sender.balance = sender_balance - value
    receiver.balance = Decimal(str(receiver.balance)) + value
    db.add(Transaction(account_number=sender.account_number, transaction_type="Transfer Sent",
                       amount=value, description=f"Transferred to account {receiver.account_number}"))
    db.add(Transaction(account_number=receiver.account_number, transaction_type="Transfer Received",
                       amount=value, description=f"Received from account {sender.account_number}"))
    db.commit()
    db.refresh(sender)
    return render_page(request, "result.html", f"₹{value:.2f} transferred successfully to account {receiver.account_number}.",
                       "success", title="Transfer Successful", account=sender)


@app.get("/close-account", response_class=HTMLResponse)
def close_account_page(request: Request):
    return render_page(request, "close_account.html")


@app.post("/close-account", response_class=HTMLResponse)
def close_account(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_valid_account(db, account_number, name, password)
    if not account:
        return render_page(request, "close_account.html", "Invalid account number, name, or password.", "error")
    if Decimal(str(account.balance)) > 0:
        return render_page(request, "close_account.html",
                           f"Please withdraw or transfer the remaining balance of ₹{account.balance:.2f} before closing the account.",
                           "error")
    db.query(Transaction).filter(Transaction.account_number == account.account_number).delete()
    db.delete(account)
    db.commit()
    return render_page(request, "result.html", f"Account {account_number} has been closed successfully.",
                       "success", title="Account Closed")


@app.get("/transactions", response_class=HTMLResponse)
def transaction_history_page(request: Request):
    return render_page(request, "transactions.html")


@app.post("/transactions", response_class=HTMLResponse)
def transaction_history(
    request: Request,
    account_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_valid_account(db, account_number, name, password)
    if not account:
        return render_page(request, "transactions.html", "Invalid account number, name, or password.", "error")
    history = (db.query(Transaction)
               .filter(Transaction.account_number == account.account_number)
               .order_by(Transaction.id.desc()).all())
    return render_page(request, "transactions.html", "Account verified.", "success",
                       account=account, history=history)
