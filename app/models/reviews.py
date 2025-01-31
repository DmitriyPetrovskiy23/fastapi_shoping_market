from app.backend.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Date, Boolean
from datetime import datetime

class Reviews(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('rating.id'))
    comment = Column(String)
    comment_date = Column(Date, default=datetime.utcnow())
    is_active = Column(Boolean, default=True)

