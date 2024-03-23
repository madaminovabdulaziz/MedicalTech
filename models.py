from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Float
from sqlalchemy.orm import relationship
from utils.db_api.database import Base, engine



class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255))
    telegram_id = Column(String(255))
    username = Column(String(255))
    phone = Column(String(255))
    role = Column(String(255))
    lang = Column(String(255))


    orders = relationship('Orders', back_populates='user')
    cart = relationship('Cart', back_populates='user')
    location = relationship('UserLocations', back_populates='user')

class UserLocations(Base):
    __tablename__ = 'user_locations'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.telegram_id'))
    latitude = Column(String(255))
    longitude = Column(String(255))
    adress = Column(String(5000))

    user = relationship('Users', back_populates='location')


class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    category_id = Column(String(255), ForeignKey('categories.id'))
    price = Column(Float)
    sterile_status = Column(String(255))
    description = Column(String(2000))
    photo_id = Column(String(1000))
    min_order = Column(String(255))



    
    order = relationship('Orders', back_populates='product')
    cart = relationship('Cart', back_populates='product')
    category = relationship("Categories", back_populates='product')



class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(255))
    product = relationship('Products', back_populates='category')




class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(5000))
    user_id = Column(String(255), ForeignKey('users.telegram_id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity_ordered = Column(Integer)
    total_price = Column(Float)
    order_date = Column(String(255))
    status = Column(String(255))


    user = relationship('Users', back_populates='orders')
    product = relationship('Products', back_populates='order')
    

class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.telegram_id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)


    user = relationship('Users', back_populates='cart')
    product = relationship('Products', back_populates='cart')




