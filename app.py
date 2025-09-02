from flask import Flask, render_template, request
import mercadopago
from dotenv import load_dotenv
import os

load_dotenv()  # lê as variáveis do .env

app = Flask(__name__)

# Credenciais do Mercado Pago (sandbox/teste)
MP_ACCESS_TOKEN = "APP_USR-561137101629095-090118-2653a3e036ad39e3bff4f771ab16a60a-2660261181"
MP_PUBLIC_KEY = "APP_USR-740f901f-9935-454e-bf84-060535202338"

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# Produtos de exemplo
PRODUTOS = {
    1: {"nome": "Pizza Grande", "preco": 59.90},
    2: {"nome": "Hambúrguer Duplo", "preco": 29.90},
    3: {"nome": "Refrigerante 2L", "preco": 12.00},
}


@app.route("/")
def home():
    return render_template("produtos.html", produtos=PRODUTOS)


@app.route("/checkout", methods=["POST"])
def checkout():
    produto_id = int(request.form.get("produto_id"))
    produto = PRODUTOS.get(produto_id)

    if not produto:
        return "Produto não encontrado", 404

    preference_data = {
        "items": [
            {
                "title": produto["nome"],
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": produto["preco"]
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:5000/sucesso",
            "failure": "http://127.0.0.1:5000/erro",
            "pending": "http://127.0.0.1:5000/pendente"
        }
        # removi "auto_return" para não dar erro no localhost
    }

    # Cria a preferência
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    # Debug: logar resposta completa
    print("Resposta Mercado Pago:", preference_response)

    preference_id = preference.get("id")
    if not preference_id:
        return f"Erro ao criar preferência: {preference_response}", 500

    return render_template(
        "checkout.html",
        preference_id=preference_id,
        public_key=MP_PUBLIC_KEY
    )
@app.route("/sucesso")
def sucesso():
    return "✅ Pagamento aprovado!"


@app.route("/erro")
def erro():
    return "❌ Pagamento falhou!"


@app.route("/pendente")
def pendente():
    return "⌛ Pagamento pendente!"


if __name__ == "__main__":
    app.run(debug=True)
