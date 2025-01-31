from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, update, func, delete
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Reviews
from app.models.rating import Rating
from app.models.products import Product
from app.backend.db_depends import get_db
from app.schemas import CreateReview
from app.routers.auth import get_current_user

router = APIRouter(prefix='/review', tags=['review'])

@router.get('/all_reviews')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Reviews).where(Reviews.is_active==True))
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return reviews.all()

@router.get('/products_reviews/{id}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], id: int):
    products_reviews=await db.scalar(select(Reviews).where(Reviews.product_id == id, Reviews.is_active == True))
    if products_reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return products_reviews

@router.post('/add_review', status_code=status.HTTP_201_CREATED)
async def add_review(db: Annotated[AsyncSession, Depends(get_db)], review_data: CreateReview, get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db.scalar(select(Product).where(Product.id == review_data.product_id))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    result = await db.execute(insert(Rating).values(
            grade = 0.0,
            user_id = get_user['id'],
            product_id =review_data.product_id,
        ).returning(Rating.id)
    )
    rating_id = result.scalar_one()
    await db.execute(insert(Reviews).values(
        user_id=get_user['id'],
        product_id=review_data.product_id,
        rating_id=rating_id,
        comment=review_data.comment,
    ))

    await db.commit()
    return review_data.comment
    avg_rating = await db.scalar(
        select(func.avg(Rating.grade))
        .where(Rating.product_id == review_data.product_id)
    )
    product.rating = avg_rating if avg_rating else 0.0

    await db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': "Successful"
    }

@router.delete('/delete_reviews')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    review_delete = await db.scalar(select(Reviews).where(Reviews.id == review_id))
    if review_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no review found'
             )
    if get_user.get('is_admin'):
        await db.execute(update(Reviews).where(Reviews.id == review_id).values(is_active = False))
        await db.execute(update(Rating).where(Rating.review_id == review_id).values(is_active = False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is succesfull'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
    
# @router.delete('/delete_ratings')
# async def delete_ratings(db: Annotated[AsyncSession, Depends(get_db)]):
#     await db.execute(delete(Rating))
#     await db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Ratings delete is succesfull'
#     }