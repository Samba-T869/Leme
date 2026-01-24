from flask import Flask, render_template, request, jsonify, redirect, url_for, request, session
import os
from datetime import datetime
from flask_cors import CORS
from models import init_db, add_payment, update_payment_status, get_paid_users, add_invitation, get_payment_by_transaction, update_user_name, get_all_users
from dotenv import load_dotenv
import requests
import uuid

load_dotenv()

app = Flask(__name__, static_folder ='static', template_folder ='templates')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_mwekemet_key')
CORS(app)

# Initialize database
init_db()

# PesaPal Configuration
PESAPAL_CONSUMER_KEY = os.getenv('PESAPAL_CONSUMER_KEY')
PESAPAL_CONSUMER_SECRET = os.getenv('PESAPAL_CONSUMER_SECRET')
PESAPAL_IPN_ID = os.getenv('PESAPAL_IPN_ID') # Get this from Pesapal Dashboard
PESAPAL_BASE_URL = "https://pay.pesapal.com/v3"

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '8ad3ud1uvu')

def get_pesapal_token():
    url = f"{PESAPAL_BASE_URL}/api/Auth/RequestToken"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "consumer_key": PESAPAL_CONSUMER_KEY,
        "consumer_secret": PESAPAL_CONSUMER_SECRET
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('token')
            
    except Exception as e:
        print(f"Token Error: {e}")
        
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin():
	if not session.get('user'):
		return redirect(url_for('login'))
	return render_template('admin.html')
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method =='POST':
		password = request.form.get('password')
		
		if password == ADMIN_PASSWORD:
			session['user'] = True
			return redirect(url_for('admin'))
			
	return render_template('login.html')
	
@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    data = request.json
    whatsapp = data.get('whatsapp')
    amount = float(data.get('amount'))
    
    # Generate confirmation token
    token = get_pesapal_token()
    if not token:
    	return jsonify({"Error": "Failed to authenticate with pesapal"}), 500
    
    merchant_reference = str(uuid.uuid4())
    
    url = f"{PESAPAL_BASE_URL}/api/Transactions/SubmitOrderRequest"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "id": merchant_reference,
        "currency": "USD", # Change to TZS if needed
        "amount": amount,
        "description": "WhatsApp Group Access",
        "callback_url": url_for('payment_callback', _external=True),
        "notification_id": PESAPAL_IPN_ID,
        "billing_address": {
            "phone_number": whatsapp
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        # Save to DB with unique tracking ID from PesaPal
        add_payment(res_data['order_tracking_id'], whatsapp, amount, "N/A", "pending")
        return jsonify({"redirect_url": res_data['redirect_url']})
    
    return jsonify({"error": "Payment creation failed"}), 400

@app.route('/payment-callback')
def payment_callback():
    tracking_id = request.args.get('OrderTrackingId')
    # In production, you'd verify status here via Pesapal API
    update_payment_status(tracking_id, 'completed')
    return render_template('success.html')

@app.route('/api/admin/paid-users', methods=['GET'])
def admin_get_paid_users():
    if not session.get('user'):
        return jsonify({"error": "Unauthorized"}), 401
    
    users = get_all_users() # Fetch from models.py
    users_list = [{"whatsapp_number": u[1], "amount": u[4], "paid_at": u[10], "status": u[6]} for u in users]
    
    return jsonify({"users": users_list})

@app.route('/api/pesapal/ipn', methods=['GET', 'POST'])
def pesapal_ipn():
	return jsonify({'status': 'received'})

@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect(url_for('login'))

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
