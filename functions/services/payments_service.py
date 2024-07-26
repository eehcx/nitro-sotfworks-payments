import stripe, os, uuid
from firebase_admin import firestore
import google.cloud.firestore
from flask import jsonify, send_file
from dotenv import load_dotenv
# Utils
from utils.firebase_storage import Storage
from utils.media_utils import MediaUtils

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

upload_storage = Storage().upload_to_firebase_storage
media_qr = MediaUtils().generate_qr_code

class PaymentService:
    @staticmethod
    def payment_sheet(pedido_id, account_stripe_id):
        firestore_client: google.cloud.firestore.Client = firestore.client()
        try:
            order_ref = firestore_client.collection('pedidos').document(pedido_id)
            order = order_ref.get().to_dict()

            customer = stripe.Customer.create(
                stripe_account=account_stripe_id
            )

            paymentIntent = stripe.PaymentIntent.create(
                amount=int(float(order['total']) * 100),
                currency='mxn',
                customer=customer.id,
                automatic_payment_methods={
                    'enabled': True,
                },
                #payment_method_types=['card', 'google_pay', 'apple_pay'],
                application_fee_amount=123,
                stripe_account=account_stripe_id,
                metadata={
                    'order_id': pedido_id
                }
            )

            return {
                'clientSecret': paymentIntent.client_secret,
                'customer': customer.id
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Error al crear la hoja de pago: {str(e)}")

    @staticmethod
    def create_payment_link(pedido_id, application_fee):
        firestore_client: google.cloud.firestore.Client = firestore.client()
        try:
            # Consultas de firebase - Consulta al key de negocio de stripe
            order_ref = firestore_client.collection('pedidos').document(pedido_id)
            order = order_ref.get().to_dict()

            branch_ref = order.get('sucursal_ref')
            branch = branch_ref.get().to_dict()

            business_ref = branch.get('negocio_ref')
            business = business_ref.get().to_dict()
            account_stripe_id = business.get('id_stripe_cuenta')

            # Consultas de firebase - Productos
            line_items = []
            order_details = order.get('detalle_pedido')
            for item in order_details:
                product_ref = item.get("producto_ref")
                quantity = item.get("cantidad")

                if product_ref:
                    product = product_ref.get().to_dict()
                    stripe_product_id = product.get('stripe_product_id')

                    prices = stripe.Price.list(product=stripe_product_id, stripe_account=account_stripe_id)
                    price_id = prices.data[0].id

                    line_items.append({
                        'price': price_id,
                        'quantity': quantity,
                    })

            payment_link = stripe.PaymentLink.create(
                line_items=line_items,
                currency='mxn',
                application_fee_amount=int(float(application_fee) * 100),
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        'url': f'https://nitro-restaurant.web.app/confirmacion?pedido_id={pedido_id}'
                    },
                },
                stripe_account=account_stripe_id,
                metadata={
                    'order_id': pedido_id
                }
            )

            qr_code_img = media_qr(payment_link.url)
            qr_code_filename = f'{uuid.uuid4()}.png'
            qr_code_url = upload_storage(qr_code_img, qr_code_filename)

            return {
                'id': payment_link.id,
                'url': payment_link.url,
                'qr_code': qr_code_url
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Error al crear el link de pago: {str(e)}")

    """
    @staticmethod
    def check_payment_link_status(payment_link_id, account_stripe_id):
        firestore_client: google.cloud.firestore.Client = firestore.client()
        try:
            payment_link = stripe.PaymentLink.retrieve(
                payment_link_id,
                stripe_account=account_stripe_id
            )
            order_id = payment_link['metadata']['order_id']
            payment_intent_id = payment_link['payment_intent']

            if payment_intent_id:
                # PaymentIntent
                payment_intent = stripe.PaymentIntent.retrieve(
                    payment_intent_id,
                    stripe_account=account_stripe_id
                )
                payment_status = payment_intent['status']

                # Actualizar estado en Firestore
                if payment_status == 'succeeded':
                    order_ref = firestore_client.collection('pedidos').document(order_id)
                    order_ref.update({'estado': True})
                elif payment_status == 'requires_payment_method':
                    print("Pago pendiente de método de pago")
                else:
                    print(f"Estado del pago: {payment_status}")

            return payment_status
        except stripe.error.StripeError as e:
            print(f"Error al recuperar el PaymentLink: {str(e)}")
            return None
        except google.cloud.exceptions.GoogleCloudError as e:
            print(f"Error al actualizar Firestore: {str(e)}")
            return None

    @staticmethod
    def check_payment_link_status(payment_link_id, account_stripe_id):
        firestore_client: google.cloud.firestore.Client = firestore.client()
        try:
            payment_link = stripe.PaymentLink.retrieve(
                payment_link_id,
                stripe_account=account_stripe_id
            )
            #order_id = payment_link['metadata']['order_id']
            payment_status = payment_link

            return payment_status
        except stripe.error.StripeError as e:
            print(f"Error al recuperar el PaymentLink: {str(e)}")
            return None
        except google.cloud.exceptions.GoogleCloudError as e:
            print(f"Error al actualizar Firestore: {str(e)}")
            return None
    """