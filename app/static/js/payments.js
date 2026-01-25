document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe
    if (window.stripePublicKey && window.stripePublicKey !== "pk_test_placeholder") {
        window.stripe = Stripe(window.stripePublicKey);
    }

    // Initialize PayPal if SDK is loaded
    if (window.paypal) {
        paypal.Buttons({
            createOrder: async function(data, actions) {
                setLoading(true);
                const amount = document.getElementById("donationAmount").value;
                const currency = getSelectedCurrency();

                try {
                    const response = await fetch("/donations/create_order", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ amount: parseFloat(amount), currency: currency, provider: "paypal" })
                    });

                    if (!response.ok) throw new Error("Order creation failed");
                    const orderData = await response.json();
                    setLoading(false);
                    return orderData.order_id;
                } catch (e) {
                    setLoading(false);
                    console.error(e);
                    showError("PayPal Error: " + e.message);
                }
            },
            onApprove: async function(data, actions) {
                setLoading(true);
                const amount = document.getElementById("donationAmount").value;
                const currency = getSelectedCurrency();

                try {
                    const response = await fetch("/donations/verify", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            provider: "paypal",
                            amount: parseFloat(amount),
                            currency: currency,
                            purpose: "Online Donation",
                            payment_data: {
                                paypal_order_id: data.orderID
                            }
                        })
                    });

                    if (response.ok) {
                        alert("Donation Successful!"); // Keep success alert or redirect immediately
                        window.location.href = "/ledger";
                    } else {
                        showError("PayPal Verification Failed");
                    }
                } catch (e) {
                    console.error(e);
                    showError("Verification Error");
                } finally {
                    setLoading(false);
                }
            },
            onError: function(err) {
                console.error(err);
                showError("PayPal Error");
                setLoading(false);
            },
            onCancel: function(data) {
                setLoading(false);
            }
        }).render('#paypal-button-container');
    }
});

function getSelectedCurrency() {
    const currencyEl = document.getElementById("currencySelect");
    return currencyEl ? currencyEl.value : "INR";
}

function toggleProviders() {
    const provider = document.querySelector('input[name="paymentProvider"]:checked').value;
    document.getElementById('razorpay-section').style.display = provider === 'razorpay' ? 'block' : 'none';
    document.getElementById('stripe-section').style.display = provider === 'stripe' ? 'block' : 'none';
    document.getElementById('paypal-section').style.display = provider === 'paypal' ? 'block' : 'none';
}

function setLoading(isLoading) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        if (isLoading) {
            spinner.classList.remove('d-none');
        } else {
            spinner.classList.add('d-none');
        }
    }
}

function showError(msg) {
    const alertBox = document.getElementById('error-alert');
    if (alertBox) {
        alertBox.textContent = msg;
        alertBox.classList.remove('d-none');
        // Auto hide after 5 seconds
        setTimeout(() => alertBox.classList.add('d-none'), 5000);
    } else {
        alert(msg);
    }
}

// --- Razorpay ---
async function initiateRazorpay() {
    setLoading(true);
    const amount = document.getElementById("donationAmount").value;
    const currency = getSelectedCurrency();

    try {
        const response = await fetch("/donations/create_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: parseFloat(amount), currency: currency, provider: "razorpay" })
        });

        if (!response.ok) throw new Error("Order creation failed");
        const order = await response.json();

        var options = {
            "key": order.key_id,
            "amount": order.amount,
            "currency": order.currency,
            "name": "Handi Temple",
            "description": "Donation",
            "order_id": order.id,
            "handler": async function (response){
                setLoading(true);
                try {
                    const verifyResponse = await fetch("/donations/verify", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            provider: "razorpay",
                            amount: parseFloat(amount),
                            currency: currency,
                            purpose: "Online Donation",
                            payment_data: {
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_signature: response.razorpay_signature
                            }
                        })
                    });

                    if (verifyResponse.ok) {
                        alert("Donation Successful!");
                        window.location.href = "/ledger";
                    } else {
                        showError("Verification Failed");
                    }
                } catch (e) {
                    showError("Verification Network Error");
                } finally {
                    setLoading(false);
                }
            },
            "modal": {
                "ondismiss": function(){
                    setLoading(false);
                }
            },
            "theme": { "color": "#198754" }
        };
        var rzp1 = new Razorpay(options);
        rzp1.open();

    } catch (e) {
        console.error(e);
        showError("Error initiating Razorpay");
        setLoading(false);
    }
    // Note: setLoading(false) for Razorpay is handled in dismiss or handler usually,
    // but we can't easily detect open success vs closed without payment.
    // 'rzp1.open()' returns immediately.
    // We rely on modal.ondismiss to clear loading.
}

// --- Stripe ---
let elements = null;
let currentStripeClientSecret = null;

async function initiateStripe() {
    if (!window.stripe) { showError("Stripe not configured"); return; }

    setLoading(true);
    const amount = document.getElementById("donationAmount").value;
    const currency = getSelectedCurrency();

    try {
        const response = await fetch("/donations/create_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: parseFloat(amount), currency: currency, provider: "stripe" })
        });

        if (!response.ok) throw new Error("Order creation failed");
        const data = await response.json();

        currentStripeClientSecret = data.client_secret;

        // Show Modal
        const modal = new bootstrap.Modal(document.getElementById('stripeModal'));
        modal.show();

        // Init Elements
        elements = window.stripe.elements({ clientSecret: currentStripeClientSecret });
        const paymentElement = elements.create('payment');
        paymentElement.mount('#payment-element');

    } catch (e) {
        console.error(e);
        showError("Error initiating Stripe");
    } finally {
        setLoading(false);
    }
}

async function confirmStripePayment() {
    if (!window.stripe || !elements) return;

    // UI: Disable button to prevent double click
    const submitBtn = document.getElementById('stripe-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";

    const { error, paymentIntent } = await window.stripe.confirmPayment({
        elements,
        confirmParams: {
            return_url: window.location.origin + "/ledger",
        },
        redirect: "if_required"
    });

    if (error) {
        document.getElementById('stripe-error-message').textContent = error.message;
        submitBtn.disabled = false;
        submitBtn.textContent = "Pay Now";
    } else if (paymentIntent && paymentIntent.status === 'succeeded') {
         const amount = document.getElementById("donationAmount").value;
         const currency = getSelectedCurrency();

         await fetch("/donations/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                provider: "stripe",
                amount: parseFloat(amount),
                currency: currency,
                purpose: "Online Donation",
                payment_data: {
                    payment_intent_id: paymentIntent.id
                }
            })
        });

        window.location.href = "/ledger";
    }
}
