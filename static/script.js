// Payment Page Functions
if (document.getElementById('paymentForm')) {
    document.addEventListener('DOMContentLoaded', function() {
        // Amount selector
        document.querySelectorAll('.amount-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.amount-option').forEach(o => o.classList.remove('selected'));
                this.classList.add('selected');
                const amount = this.getAttribute('data-amount');
                document.getElementById('amount').value = amount;
                document.getElementById('displayAmount').textContent = amount;
                document.getElementById('payButton').innerHTML = 
                    `<i class="fas fa-lock"></i> Pay & Join Group - $${amount}`;
            });
        });
        
        // Payment form submission
        document.getElementById('paymentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const whatsappNumber = document.getElementById('whatsappNumber').value;
            const amount = document.getElementById('amount').value;
            
            if (!validateWhatsAppNumber(whatsappNumber)) {
                showStatus('Please enter a valid WhatsApp number with country code (e.g., +1234567890)', 'error');
                return;
            }
            
            showStatus('Creating payment request...', 'info');
            
            try {
                const response = await fetch(`${API_BASE_URL}/create-payment`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        whatsapp_number: whatsappNumber,
                        amount: parseFloat(amount)
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showPaymentModal(data);
                } else {
                    showStatus('Error creating payment: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch (error) {
                showStatus('Network error. Please try again.', 'error');
                console.error('Payment error:', error);
            }

// Common Functions
function validateWhatsAppNumber(number) {
    // Basic validation for international phone numbers
    const regex = /^\+[1-9]\d{1,14}$/;
    return regex.test(number);
}

function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('payment-status') || 
                         document.getElementById('adminStatus') || 
                         document.getElementById('loginStatus');
    
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = 'status-message ' + type;
        statusElement.style.display = 'block';
        
        if (type !== 'info') {
            setTimeout(() => {
                statusElement.style.display = 'none';
            }, 5000);
        }
    }
}

function showPaymentModal(paymentData) {
    const modal = document.getElementById('paymentModal');
    const details = document.getElementById('paymentDetails');
    
    details.innerHTML = `
        <div style="text-align: center;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Payment Details</h3>
                <p><strong>Transaction ID:</strong> ${paymentData.transaction_id}</p>
                <p><strong>Amount:</strong> $${paymentData.amount}</p>
                <p><strong>WhatsApp:</strong> ${paymentData.whatsapp_number}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <div style="background: white; padding: 15px; border-radius: 10px; border: 2px dashed #667eea;">
                    <p><strong>Complete Payment:</strong></p>
                    <p>1. Send $${paymentData.amount} to our payment account</p>
                    <p>2. Use transaction ID: <code>${paymentData.transaction_id}</code></p>
                    <p>3. Payment will be verified automatically</p>
                </div>
            </div>
            
            <div id="paymentQR" style="margin: 20px 0;">
                <!-- QR Code would go here in production -->
                <p><i class="fas fa-qrcode fa-3x"></i></p>
                <p>Scan to pay</p>
            </div>
        </div>
    `;
    
    modal.classList.add('active');
    
    // In production, you would start polling for payment status
    // const pollInterval = setInterval(() => checkPaymentStatus(paymentData.transaction_id), 5000);
    // Store interval ID for cleanup
    // modal.dataset.pollInterval = pollInterval;
}



async function loadPaidUsers() {
    const token = localStorage.getItem('adminToken');
    if (!token) return;
    
    try {
        const password = atob(token);
        const response = await fetch(`${API_BASE_URL}/admin/paid-users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password })
        });
        
        if (response.ok) {
            const data = await response.json();
            updateUsersTable(data.users);
            updateStats(data.users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showStatus('Error loading users', 'error');
    }
}

function updateUsersTable(users) {
    const tableBody = document.getElementById('usersTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (users.length === 0) {
        tableBody.innerHTML = `
        <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <i class="fas fa-users-slash fa-2x" style="color: #6c757d; margin-bottom: 10px;"></i>
                    <p>No paid users yet</p>
                </td>
            </tr>
        `;
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        
        const date = new Date(user.paid_at);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        row.innerHTML = `
            <td><i class="fab fa-whatsapp" style="color: #25D366;"></i> ${user.whatsapp_number}</td>
            <td><strong>$${user.amount}</strong></td>
            <td>${formattedDate}</td>
            <td><span class="payment-method">${user.payment_method || 'N/A'}</span></td>
            <td id="invite-${user.whatsapp_number.replace('+', '')}">
                <button onclick="showInviteForm('${user.whatsapp_number}')" 
                        class="send-invite-btn" style="padding: 5px 10px;">
                    <i class="fas fa-paper-plane"></i> Send Invite
                </button>
            </td>
            <td>
                <button onclick="copyNumber('${user.whatsapp_number}')" 
                        style="background: #6c757d; color: white; border: none; 
                               padding: 5px 10px; border-radius: 5px; cursor: pointer;">
                    <i class="fas fa-copy"></i>
        </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}
            
