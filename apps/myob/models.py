from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from apps.myconstant import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql://" + MDB_USERNAME + ":" + MDB_PASSWORD + "@localhost/mmc_db"
)
db = SQLAlchemy(app)


class Invoice(db.Model):
    __tablename__ = "Invoice"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(80), unique=True)
    inv_no = db.Column(db.String(80), unique=True)
    invoice_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    item = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200))
    units = db.Column(db.Integer, unique=True)
    tax_type = db.Column(db.String(80), unique=True)
    amount = db.Column(db.Integer, unique=True)
    unit_price = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Invoice %r>" % self.name


class Customer(db.Model):
    __tablename__ = "Customer"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=True)
    last_name = db.Column(db.String(80), unique=True)
    position = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    phone = db.Column(db.String(80), unique=True)
    mobile = db.Column(db.String(80), unique=True)
    fax = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(80), unique=True)
    state = db.Column(db.String(80), unique=True)
    country = db.Column(db.String(80), unique=True)
    postcode = db.Column(db.String(80), unique=True)
    notes = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Customer %r>" % self.first_name


class Employee(db.Model):
    __tablename__ = "Employee"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=True)
    last_name = db.Column(db.String(80), unique=True)
    gender = db.Column(db.String(80), unique=True)
    birth_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    finish_date = db.Column(db.DateTime)
    job_title = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(80), unique=True)
    state = db.Column(db.String(80), unique=True)
    country = db.Column(db.String(80), unique=True)
    postcode = db.Column(db.String(80), unique=True)
    employee_id = db.Column(db.String(80), unique=True)
    phone = db.Column(db.String(80), unique=True)
    mobile = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    tax_file_number = db.Column(db.String(80), unique=True)
    hourly_rate = db.Column(db.String(80), unique=True)
    annual_salary = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Employee %r>" % self.first_name


class Item(db.Model):
    __tablename__ = "Item"

    id = db.Column(db.Integer, primary_key=True)
    item_number = db.Column(db.String(80), unique=True)
    item_name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200))
    sale_price = db.Column(db.String(80), unique=True)
    unit = db.Column(db.String(80), unique=True)
    unit_measure = db.Column(db.String(80), unique=True)
    tax_type = db.Column(db.String(80), unique=True)
    unit_description = db.Column(db.String(200))
    buy_price = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Item %r>" % self.item_name


class Journal(db.Model):
    __tablename__ = "Journal"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    ref_no = db.Column(db.String(80), unique=True)
    account_number = db.Column(db.Integer, unique=True)
    account_name = db.Column(db.String(80), unique=True)
    debit = db.Column(db.String(80), unique=True)
    credit = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Journal %r>" % self.ref_no


class Bill(db.Model):
    __tablename__ = "Bill"

    id = db.Column(db.Integer, primary_key=True)
    supplier = db.Column(db.String(80), unique=True)
    bill_no = db.Column(db.String(80), unique=True)
    issue_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    amounts_are = db.Column(db.String(80), unique=True)
    item = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200))
    allocate_to = db.Column(db.String(80), unique=True)
    quantity = db.Column(db.String(80), unique=True)
    unit_price = db.Column(db.String(80), unique=True)
    tax_type = db.Column(db.String(80), unique=True)
    amount = db.Column(db.String(80), unique=True)
    notes = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Bill %r>" % self.supplier


class SpendMoney(db.Model):
    __tablename__ = "Spend_Money"

    id = db.Column(db.Integer, primary_key=True)
    pay_from = db.Column(db.String(80), unique=True)
    pay_to = db.Column(db.String(80), unique=True)
    notes = db.Column(db.String(80), unique=True)
    date = db.Column(db.DateTime)
    ref_no = db.Column(db.String(80), unique=True)
    amounts_are = db.Column(db.String(80), unique=True)
    attachment = db.Column(db.String(80), unique=True)
    allocate_to = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.Integer)
    tax_rate = db.Column(db.String(80), unique=True)
    tax_amount = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<SpendMoney %r>" % self.pay_from


class ReceivedMoney(db.Model):
    __tablename__ = "Received_Money"

    id = db.Column(db.Integer, primary_key=True)
    deposit_into = db.Column(db.String(80), unique=True)
    notes = db.Column(db.String(80), unique=True)
    date = db.Column(db.DateTime)
    ref_no = db.Column(db.String(80), unique=True)
    amounts_are = db.Column(db.String(80), unique=True)
    cheque_no = db.Column(db.String(80), unique=True)
    payer = db.Column(db.String(80), unique=True)
    allocate_to = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.String(80), unique=True)
    tax_rate = db.Column(db.String(80), unique=True)
    tax_amount = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<ReceivedMoney %r>" % self.deposit_into


class ChartOfAccount(db.Model):
    __tablename__ = "Chart_Of_Account"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(80), unique=True, nullable=False)
    account_type = db.Column(db.String(80), unique=True)
    tax_type = db.Column(db.String(80), unique=True)
    status = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<ChartOfAccount %r>" % self.account_name


class TrialBalance(db.Model):
    __tablename__ = "Trial_Balance"

    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.Integer, unique=True, nullable=False)
    account_name = db.Column(db.String(80), unique=True, nullable=False)
    debit = db.Column(db.String(80), unique=True, nullable=False)
    credit = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return "<TrialBalance %r>" % self.ref_no
