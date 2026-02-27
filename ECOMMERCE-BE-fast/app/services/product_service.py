"""
Product Service - Xử lý logic quản lý sản phẩm
Admin: CRUD sản phẩm
User/Guest: Xem sản phẩm, tìm kiếm, lọc
"""
from fastapi import HTTPException, status, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select, or_
from uuid import UUID
from typing import List, Dict, Any, Annotated, Optional
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from app.models.product_model import (
    Product,
    ProductIn,
    ProductOut,
    ProductDetailOut,
    ProductResponseOut,
)
from app.models.product_detail_model import (
    ProductDetail,
    ProductDetailIn,
    ProductDetailOut,
)
from app.models.product_image_model import ProductImage
from app.repositories.product_repository import ProductRepository
from app.utils.response_helper import ResponseHandler
import math

class ProductService:
    """Service quản lý sản phẩm"""

    def __init__(self, repository: Annotated[ProductRepository, Depends()]):
        self.repository = repository

    # ==================== GUEST/USER FUNCTIONS ====================

    def get_all_products(
        self,
        session: Session,
        category_id: UUID | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """[PUBLIC] Lấy danh sách sản phẩm"""
        products = self.repository.get_all(
            session=session,
            category_id=category_id if category_id else None,
            page=page if page else 1,
            limit=limit if limit else 20,
        )
        response = {"data": []}
        for product in products:
            response["data"].append(
                {
                    **product.model_dump(),
                    "images": [img.model_dump() for img in product.images],
                }
            )

        response.update(
            {
                "pagination": {
                    "page": page,
                    "pageSize": limit,
                    "total_item": len(response["data"]),
                    "totalPages": math.ceil(len(response["data"]) / int(limit))
                    if limit > 0
                    else 0,
                }
            }
        )
        return JSONResponse(jsonable_encoder(response), 200)

    def get_product_by_id(self, product_id: UUID, session: Session) -> Dict[str, Any]:
        """[PUBLIC] Lấy chi tiết sản phẩm"""
        product = self.repository.get_by_id(product_id=product_id, session=session)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sản phẩm không tồn tại"
            )
        res = {
            **product.model_dump(),
            "images": [img.model_dump() for img in product.images],
            "product_details": [
                detail.model_dump() for detail in product.product_details
            ],
        }
        return JSONResponse(jsonable_encoder(res), 200)

    def get_products_by_category(
        self, category_id: UUID, session: Session, skip: int = 0, limit: int = 20
    ) -> List[ProductOut]:
        """[PUBLIC] Lấy sản phẩm theo danh mục"""
        products = self.repository.get_by_category(
            skip=skip, limit=limit, category_id=category_id, session=session
        )

        return [ProductOut.model_validate(p) for p in products]

    def search_products(
        self, keyword: str, session: Session, skip: int = 0, limit: int = 20
    ) -> Dict[str, Any]:
        """[PUBLIC] Tìm kiếm sản phẩm theo tên hoặc mô tả"""
        products = self.repository.search(
            keyword=keyword, session=session, skip=skip, limit=limit
        )
        response = {"data": []}
        for product in products:
            response["data"].append(
                {
                    **product.model_dump(),
                    "images": [img.model_dump() for img in product.images],
                }
            )
        response.update(
            {
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total_item": len(response["data"]),
                }
            }
        )
        return JSONResponse(jsonable_encoder(response), 200)

    # ==================== ADMIN FUNCTIONS - PRODUCT ====================

    def create_product(
        self,
        session: Session,
        name: str,
        description: str,
        price: str,
        category_id: UUID,
        files: List[UploadFile],
    ) -> Dict[str, Any]:
        """[ADMIN] Tạo sản phẩm mới"""
        product = Product(
            name=name, description=description, price=price, category_id=category_id
        )
        images = []
        for file in files:
            result = upload(file.file)
            if result:
                thumbnail, _ = cloudinary_url(
                    result["public_id"],
                    format="jpg",
                    crop="fill",
                    width=100,
                    height=100,
                )
                image = ProductImage(
                    cloudinary_public_id=result["public_id"],
                    url=result["secure_url"],
                    thumbnail_url=thumbnail,
                    product_id=product.id,
                )
                images.append(image)
        product.images = images

        data = self.repository.create(session=session, product=product)

        if data:
            product_data = data.model_dump()
            product_data["images"] = [img.model_dump() for img in product.images]
            return ResponseHandler.success(
                "Tạo sản phẩm thành công", {"product": product_data}, status=200
            )

    def update_product(
        self, product_id: UUID, data: ProductIn, session: Session
    ) -> Dict[str, Any]:
        """[ADMIN] Cập nhật sản phẩm"""
        product = self.repository.get_by_id(product_id=product_id, session=session)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sản phẩm không tồn tại"
            )

        # Cập nhật các fields
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        updated_product = self.repository.update(session=session, product=product)

        return {
            "message": "Cập nhật sản phẩm thành công",
            "product": ProductOut.model_validate(updated_product),
        }

    def delete_product(self, product_id: UUID, session: Session) -> Dict[str, str]:
        """[ADMIN] Xóa sản phẩm"""
        product = self.repository.get_by_id(product_id=product_id, session=session)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sản phẩm không tồn tại"
            )

        self.repository.delete(product=product, session=session)

        return JSONResponse("Xóa sản phẩm thành công", status_code=status.HTTP_200_OK)

    # ==================== ADMIN FUNCTIONS - PRODUCT DETAIL ====================

    def get_product_details(self, product_id: UUID, session: Session) -> Dict[str, Any]:
        """[ADMIN] Lấy tất cả chi tiết sản phẩm"""
        # Kiểm tra sản phẩm tồn tại
        product = self.repository.get_by_id(product_id=product_id, session=session)
        if not product:
            return JSONResponse("Sản phẩm không tồn tại", 404)

        details = self.repository.get_details_by_product(
            product_id=product_id, session=session
        )

        return JSONResponse(jsonable_encoder(details), 200)

    def add_product_detail(
        self, product_id: UUID, data: ProductDetailIn, session: Session
    ) -> Dict[str, Any]:
        """[ADMIN] Thêm chi tiết sản phẩm"""
        # Kiểm tra product tồn tại
        product = self.repository.get_by_id(product_id=product_id, session=session)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sản phẩm không tồn tại"
            )

        # Tạo ProductDetail
        detail = ProductDetail(product_id=product_id, **data.model_dump())

        res = self.repository.create_detail(detail=detail, session=session)

        if res:
            return {
                "message": "Tạo chi tiết sản phẩm thành công",
                "detail": ProductDetailOut.model_validate(res),
            }

    def update_product_detail(
        self, product_id: UUID, detail_id: UUID, data: ProductDetailIn, session: Session
    ) -> Dict[str, Any]:
        """[ADMIN] Cập nhật chi tiết sản phẩm"""
        detail = self.repository.get_detail_by_id(detail_id=detail_id, session=session)

        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chi tiết sản phẩm không tồn tại",
            )

        # Kiểm tra product_id match
        if detail.product_id != product_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chi tiết này không thuộc sản phẩm",
            )

        # Cập nhật các fields
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(detail, key, value)

        updated_detail = self.repository.update_detail(detail=detail, session=session)
        
        return {
            "message": "Cập nhật chi tiết sản phẩm thành công",
            "detail": ProductDetailOut.model_validate(updated_detail),
        }

    def delete_product_detail(
        self, product_id: UUID, detail_id: UUID, session: Session
    ) -> Dict[str, str]:
        """[ADMIN] Xóa chi tiết sản phẩm"""
        detail = self.repository.get_detail_by_id(detail_id=detail_id, session=session)

        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chi tiết sản phẩm không tồn tại",
            )

        # Kiểm tra product_id match
        if detail.product_id != product_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chi tiết này không thuộc sản phẩm",
            )

        self.repository.delete_detail(detail=detail, session=session)

        return {"message": "Xóa chi tiết sản phẩm thành công"}