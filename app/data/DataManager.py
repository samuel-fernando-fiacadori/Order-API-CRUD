# --- app/data/DataManager.py ---
# Aqui ficam seus modelos e a classe de gerenciamento.
# O gerenciador agora aceita uma sessão como parâmetro.

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Type

# Define a base para os modelos
Base = declarative_base()

class Product(Base):
    __tablename__ = 'Product'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    price = sa.Column(sa.Float, default=0.00)

    # Método para converter o objeto em um dicionário serializável
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }

class Order(Base):
    __tablename__ = 'Order'
    id = sa.Column(sa.Integer, primary_key=True)
    client_name = sa.Column(sa.String(100), nullable=False)
    product_id = sa.Column(sa.Integer, sa.ForeignKey('Product.id'), nullable=False)
    # Adicionando a coluna client_house de volta
    client_house = sa.Column(sa.String(200), nullable=False)

    # Método para converter o objeto em um dicionário serializável
    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'product_id': self.product_id,
            'client_house': self.client_house
        }

class BaseManager:
    """Gerenciador genérico para interações com o banco de dados."""
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, item_id: int):
        return self.session.query(self.model).filter_by(id=item_id).first()

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, item_id, **kwargs):
        obj = self.get_by_id(item_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.session.commit()
            return obj
        return None

    def delete(self, item_id):
        obj = self.get_by_id(item_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False