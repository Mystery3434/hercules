from flask import Blueprint
from flask import render_template, abort, request, current_app, url_for
from flask_login import login_required, current_user
from GRETutoring.models import Event, User
from GRETutoring import db
import stripe


transactions = Blueprint('transactions', __name__)



@transactions.route('/buy_credits')
@login_required
def buy_credits():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    if current_user.role == "Tutor":
        abort(403)
    #form = BuyCreditsForm()

    return render_template("buy_credits.html", title="Buy Credits")

@transactions.route('/stripe_pay')
def stripe_pay():
    num_credits = int(request.args.get("num_credits"))
    classes = Event.query.filter_by(student_id=current_user.id).all()
    discount_class = False
    if not classes and current_user.credits==0:
        discount_class = True
    if discount_class:
        discounted_credits = 1
        num_credits -= 1
    else:
        discounted_credits = 0
    items = []
    if discount_class:
        items.append({'price': 'price_1Jl84OIGcrQ8gAqRRF66tpPF',
            'quantity': discounted_credits})

    items.append({
            'price': 'price_1JkLeHIGcrQ8gAqR7zeofeNi',
            'quantity': num_credits,
        })
    total_credits = num_credits + discounted_credits
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url=url_for('transactions.successful_payment', _external=True) + '?num_credits=' + str(total_credits) + '&session_id={CHECKOUT_SESSION_ID}'
        ,
        cancel_url=url_for('transactions.buy_credits', _external=True),
    )
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': current_app.config['STRIPE_PUBLIC_KEY']
    }



@transactions.route('/payment')
def payment():
    return render_template("payment.html")

@transactions.route('/successful_payment')
def successful_payment():
    num_credits = int(request.args.get('num_credits'))
    current_user.credits += num_credits
    db.session.commit()
    return render_template("successful_payment.html", num_credits = num_credits)