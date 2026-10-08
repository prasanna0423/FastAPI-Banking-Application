# FastAPI Banking Application

A simple Banking Application developed using Python, FastAPI, SQLAlchemy, SQLite, HTML, CSS, and JavaScript.

## Features

* User Registration and Login
* Secure Password Hashing
* Account Management
* Check Account Balance
* Deposit Money
* Withdraw Money
* Transfer Money
* Transaction History

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* SQLite
* HTML
* CSS
* JavaScript
* Uvicorn

## How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

http://127.0.0.1:8000

API Documentation:

http://127.0.0.1:8000/docs

## Database

SQLite database with SQLAlchemy is used for storing banking application data.

## Security

Passwords are securely hashed using PBKDF2-HMAC-SHA256.

## Project Purpose

This project was developed as a learning and portfolio project to practice FastAPI, database integration, authentication, CRUD operations, and backend web application development.
