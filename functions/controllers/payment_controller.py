import stripe, os
from flask import request, jsonify, send_file, url_for
from services.payments_service import PaymentService
from dotenv import load_dotenv

load_dotenv()

payment_service = PaymentService()

class PaymentController:
    @staticmethod
    def payment_sheet_controller():
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        account_stripe_id = data.get('account_stripe_id')

        if not pedido_id or not account_stripe_id:
            return jsonify({'error': 'Parámetros faltantes'}), 400
        
        try:
            response_data = payment_service.payment_sheet(pedido_id, account_stripe_id)
            return jsonify(response_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def create_payment_link_controller():
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        application_fee = data.get('application_fee')

        try:
            response_data = payment_service.create_payment_link(pedido_id, application_fee)
            return jsonify(response_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400