// PayPal Integration Script

// Function to show error messages
function showError(message) {
    console.error('Payment Error:', message);
    const container = document.getElementById('paypal-button-container');
    if (container) {
        container.innerHTML = `
            <div class="bg-red-50 border-l-4 border-red-400 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700">${message}</p>
                        <button onclick="window.location.reload()" class="mt-2 text-sm font-medium text-red-600 hover:text-red-500">
                            Réessayer <span aria-hidden="true">&rarr;</span>
                        </button>
                    </div>
                </div>
            </div>`;
    } else {
        console.error('Error container not found');
        const shouldReload = confirm('Erreur: ' + message + '\n\nVoulez-vous réessayer?');
        if (shouldReload) {
            window.location.reload();
        }
    }
}

// Initialize PayPal Buttons
function initializePayPalButtons() {
    console.log('Initializing PayPal buttons...');
    
    const container = document.getElementById('paypal-button-container');
    if (!container) {
        console.error('PayPal container not found');
        showError('Erreur d\'initialisation du paiement. Veuillez réessayer.');
        return;
    }
    
    // Check if PayPal is loaded
    if (typeof paypal === 'undefined') {
        showError('Le système de paiement n\'a pas pu être chargé. Veuillez réessayer.');
        return;
    }
    
    try {
        // Clear any existing buttons
        container.innerHTML = '';
        
        // Create PayPal button
        paypal.Buttons({
            // Button styling
            style: {
                layout: 'vertical',
                color: 'blue',
                shape: 'rect',
                label: 'pay',
                height: 45,
                tagline: false
            },
            
            // Create order on server
            createOrder: function(data, actions) {
                console.log('Creating PayPal order...');
                
                // Show loading state
                container.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                        <p class="mt-2 text-sm text-gray-600">Création de la commande...</p>
                    </div>`;
                
                // Create order on server
                return fetch('/create-paypal-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({
                        unique_id: document.getElementById('unique-id').value,
                        amount: parseFloat(document.getElementById('total-amount').value)
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(text || 'Failed to create order');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Order created:', data);
                    if (!data.id) {
                        throw new Error('No order ID received');
                    }
                    return data.id;
                })
                .catch(error => {
                    console.error('Error creating order:', error);
                    showError('Erreur lors de la création de la commande. Veuillez réessayer.');
                    throw error; // Re-throw to be caught by PayPal
                });
            },
            
            // Handle successful payment approval
            onApprove: function(data, actions) {
                console.log('Capturing PayPal order:', data.orderID);
                
                // Show processing state
                container.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
                        <p class="mt-2 text-sm text-gray-600">Traitement du paiement...</p>
                    </div>`;
                
                // Send capture request to server
                return fetch('/capture-paypal-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({
                        orderID: data.orderID,
                        unique_id: document.getElementById('unique-id').value
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(text || 'Failed to capture order');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Payment successful:', data);
                    // Redirect to success page
                    window.location.href = data.redirect_url || '/payment/success';
                })
                .catch(error => {
                    console.error('Error capturing payment:', error);
                    showError('Erreur lors du traitement du paiement. Veuillez réessayer.');
                });
            },
            
            // Handle errors
            onError: function(err) {
                console.error('PayPal error:', err);
                showError('Une erreur est survenue avec le système de paiement. Veuillez réessayer.');
            },
            
            // Handle cancellation
            onCancel: function(data) {
                console.log('Payment cancelled:', data);
                // Reset the button
                initializePayPalButtons();
            }
        }).render('#paypal-button-container');
        
        console.log('PayPal buttons initialized successfully');
        
    } catch (error) {
        console.error('Error initializing PayPal buttons:', error);
        showError('Erreur d\'initialisation du paiement. Veuillez réessayer.');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded, starting PayPal integration...');
    
    // Add hidden inputs for template variables
    const uniqueIdInput = document.createElement('input');
    uniqueIdInput.type = 'hidden';
    uniqueIdInput.id = 'unique-id';
    uniqueIdInput.value = '{{ unique_id }}';
    document.body.appendChild(uniqueIdInput);
    
    const totalAmountInput = document.createElement('input');
    totalAmountInput.type = 'hidden';
    totalAmountInput.id = 'total-amount';
    totalAmountInput.value = '{{ "%.2f"|format(total_amount) }}';
    document.body.appendChild(totalAmountInput);
    
    // Check if SDK is already loaded
    if (typeof paypal !== 'undefined') {
        console.log('PayPal SDK already loaded, initializing buttons...');
        initializePayPalButtons();
        return;
    }
    
    // Otherwise, wait for the SDK to load
    console.log('Waiting for PayPal SDK to load...');
    
    // Set a timeout to handle cases where the SDK fails to load
    const loadTimeout = setTimeout(function() {
        if (typeof paypal === 'undefined') {
            console.error('PayPal SDK failed to load within timeout');
            showError('Le système de paiement a mis trop de temps à se charger. ' +
                     'Veuillez rafraîchir la page ou essayer plus tard.');
        }
    }, 10000); // 10 seconds timeout
    
    // Listen for the PayPal SDK to be loaded
    window.addEventListener('paypal-sdk-loaded', function() {
        clearTimeout(loadTimeout);
        console.log('PayPal SDK loaded via event, initializing buttons...');
        if (typeof paypal !== 'undefined') {
            initializePayPalButtons();
        }
    });
});
