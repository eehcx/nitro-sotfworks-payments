import stripe, os
from flask import request, jsonify
from services.webhook_service import WebhookService
from dotenv import load_dotenv

load_dotenv()

webhook_service = WebhookService()

class WebhookController:
    @staticmethod
    def handle_webhook_controller():
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')

        try:
            event = webhook_service.handle_webhook(payload, sig_header, endpoint_secret)
            return jsonify({'status': 'success'}), 200
        except ValueError:
            return jsonify({'error': 'Carga no válida'}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({'error': 'Firma no válida'}), 400
        except Exception as e:
            return jsonify({'Error': str(e)}), 400