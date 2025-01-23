from app.backend.db import Base
from sqlalchemy import Column, Integer, ForeignKey, Float, Boolean


class Rating(Base):
    __tablename__='rating'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)