from flask import Blueprint
from flask import render_template



transactions = Blueprint('transactions', __name__)


@transactions.route('/payment')
def payment():
    return render_template("payment.html")

@transactions.route('/successful_payment')
def successful_payment():
    return render_template("successful_payment.html")