from app.payment_providers.razorpay_provider import RazorpayProvider
from app.payment_providers.stripe_provider import StripeProvider
from app.payment_providers.paypal_provider import PayPalProvider

def get_payment_provider(provider_name: str):
    if provider_name == "razorpay":
        return RazorpayProvider()
    elif provider_name == "stripe":
        return StripeProvider()
    elif provider_name == "paypal":
        return PayPalProvider()
    else:
        raise ValueError(f"Unknown payment provider: {provider_name}")
