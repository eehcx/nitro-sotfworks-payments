from flask import Blueprint
from controllers.payment_controller import PaymentController

payment_bp = Blueprint('payment_bp', __name__)

payment_bp.route('/payment', methods=['POST'])(PaymentController.payment_sheet_controller)
payment_bp.route('/payment-link', methods=['POST'])(PaymentController.create_payment_link_controller)