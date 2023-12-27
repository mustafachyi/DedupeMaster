from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit
from threading import Thread
import stripe
import random
import string
import time
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keys.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'poolclass': NullPool}
db = SQLAlchemy(app)
Bootstrap(app)
socketio = SocketIO(app)

class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)

with app.app_context():
    db.create_all()

def validate_stripe_key(stripe_key):
    stripe.api_key = stripe_key
    try:
        stripe.Balance.retrieve()
        return True
    except stripe.error.AuthenticationError:
        print("AuthenticationError: Invalid API key.")
        return False
    except stripe.error.APIConnectionError:
        print("APIConnectionError: Network communication with Stripe failed.")
        return False
    except stripe.error.StripeError as e:
        print(f"StripeError: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def create_random_stripe_key(prefix, length):
    return prefix + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_and_check_keys():
    verified_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
    if not validate_stripe_key(verified_key):
        print("Unable to validate the API. Please check your verified key.")
        return

    print("API validation successful. Initiating key creation in 5 seconds...")
    time.sleep(5)

    unique_keys = set()

    while True:
        stripe_key = create_random_stripe_key('sk_live_', 24)
        if stripe_key in unique_keys:
            continue
        unique_keys.add(stripe_key)

        key_validity = validate_stripe_key(stripe_key)

        if key_validity:
            with app.app_context():
                new_key = Key(key=stripe_key)
                db.session.add(new_key)
                db.session.commit()
            socketio.emit('new_key', {'key': stripe_key}, namespace='/test')

Thread(target=generate_and_check_keys).start()

@app.route('/')
def home():
    keys = Key.query.all()
    return render_template('index.html', keys=keys)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
