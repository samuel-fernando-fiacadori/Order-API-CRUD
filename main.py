from flask import Flask, jsonify, request
from app.data.DataManager import BaseManager, Order, Product, Base
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session

app = Flask(__name__)

# --- Configuração do Banco de Dados ---
# Conexão e criação das tabelas fora da função de requisição para otimização
engine = sa.create_engine('sqlite:///app/data/database.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """
    Função para obter uma nova sessão de banco de dados para cada requisição.
    Isso é uma prática recomendada para evitar problemas de concorrência.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints para a API ---

@app.route('/product/get', methods=['GET'])
def product_getall():
    # Usa 'next' para obter a próxima sessão do gerador
    db = next(get_db_session())
    product_manager = BaseManager(db, Product)
    products = product_manager.get_all()
    # Converte a lista de objetos em uma lista de dicionários
    return jsonify([p.to_dict() for p in products])

@app.route('/order/get', methods=['GET'])
def order_getall():
    db = next(get_db_session())
    order_manager = BaseManager(db, Order)
    orders = order_manager.get_all()
    # Converte a lista de objetos em uma lista de dicionários
    return jsonify([o.to_dict() for o in orders])

@app.route('/product/get/<int:_id>', methods=['GET'])
def product_getid(_id: int):
    db = next(get_db_session())
    product_manager = BaseManager(db, Product)
    product = product_manager.get_by_id(_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"message": "Product not found"}), 404

@app.route('/order/get/<int:_id>', methods=['GET'])
def order_getit(_id: int):
    db = next(get_db_session())
    order_manager = BaseManager(db, Order)
    order = order_manager.get_by_id(_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"message": "Order not found"}), 404

@app.route('/product/add', methods=['POST'])
def product_create():
    # Obtém os dados JSON enviados na requisição
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"message": "Invalid data"}), 400

    db = next(get_db_session())
    product_manager = BaseManager(db, Product)
    try:
        new_product = product_manager.create(name=data['name'], price=data['price'])
        return jsonify(new_product.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Error creating product: {str(e)}"}), 500

@app.route('/order/add', methods=['POST'])
def order_create():
    data = request.get_json()
    if not data or 'client_name' not in data or 'product_id' not in data or 'client_house' not in data:
        return jsonify({"message": "Invalid data"}), 400
    
    db = next(get_db_session())
    order_manager = BaseManager(db, Order)
    try:
        new_order = order_manager.create(client_name=data['client_name'], product_id=data['product_id'], client_house=data['client_house'])
        return jsonify(new_order.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Error creating order: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()