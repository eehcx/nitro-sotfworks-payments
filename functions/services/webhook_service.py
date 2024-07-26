import stripe
from firebase_admin import firestore
import google.cloud.firestore

"""
Webhook personalizado:
    Necesita mas complejidad para manejar todas las 
    solicitudes webhook correctamente, ejemplo:
        - Creación de productos
        - Creación de links de pago
        - Creación de clientes
        -Etc
    Se puede considerar convertir el webhook en una 
    capa de la API, por el momento no se tocara mas
    del webhook.

    Pd: Recuerda que este end-point una vez este lis-
    to tendra que ponerse en el punto de conexion del
    webhook de stripe.
"""

class WebhookService:
    @staticmethod
    def handle_webhook(payload, sig_header, endpoint_secret):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )

            if event['type'] == 'payment_link.payment_intent.created':
                payment_intent = event['data']['object']
                print('Payment Intent creado:', payment_intent)
            elif event['type'] == 'payment_link.payment_intent.succeeded':
                payment_intent = event['data']['object']
                WebhookService.process_payment_intent_succeeded(payment_intent)
            return event
        except ValueError as e:
            print(f"ValueError: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            print(f"SignatureVerificationError: {str(e)}")
            raise

    @staticmethod
    def process_payment_intent_succeeded(payment_intent):
        firestore_client: google.cloud.firestore.Client = firestore.client()
        try:
            order_id = payment_intent['metadata']['order_id']
            order_ref = firestore_client.collection('pedidos').document(order_id)
            order_ref.update({'estado': True})
        except KeyError as e:
            print(f"Error: Metadata 'order_id' no encontrada en el payment_intent: {e}")
        except Exception as e:
            print(f"Error al procesar el payment intent: {e}")

    @staticmethod
    def process_payment_intent_failed(payment_intent):
        print(f"Pago fallido: {payment_intent['id']}")