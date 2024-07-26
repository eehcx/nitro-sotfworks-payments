from flask import Flask
# Librerías de firebase
import firebase_admin
from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials
# Paquetes
from routes.payment import payment_bp
from routes.webhook import webhook_bp

cred = credentials.ApplicationDefault() #credentials.Certificate('credentials.json') 
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.register_blueprint(payment_bp)
app.register_blueprint(webhook_bp)

@https_fn.on_request()
def stripe(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()

# Main de la aplicación
if __name__ == '__main__':
    app.run() #debug=True