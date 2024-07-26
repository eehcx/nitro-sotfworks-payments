from flask import Blueprint
from controllers.webhook_controller import WebhookController

webhook_bp = Blueprint('webhook_bp', __name__)

webhook_bp.route('/webhook', methods=['POST'])(WebhookController.handle_webhook_controller)