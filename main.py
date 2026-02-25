"""
Main Application - E-Commerce API
FastAPI application với phân quyền: Admin, User, Guest
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Import routers
from app.routers.auth_router import authRouter
from app.routers.user_routes import userRouter
from app.routers.category_router import categoryRouter
from app.routers.product_router import productRouter
from app.routers.cart_router import cartRouter
from app.routers.order_router import orderRouter
from app.routers.address_router import addressRouter
from app.routers.checkout_router import checkoutRouter
from app.routers.goship_router import goshipRouter
from app.core.cloudinary import cloud_config
app = FastAPI(
    title="E-Commerce API",
    description="""
    API cho hệ thống thương mại điện tử
    
    ## Phân quyền:
    - **Admin (role_id=0)**: Toàn quyền quản lý
    - **User (role_id=1)**: Mua hàng, quản lý đơn hàng cá nhân
    - **Guest**: Xem sản phẩm, danh mục (không cần đăng nhập)
    """,
    version="1.0.0"
)

cloud_config()
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API prefix
PREFIX = "/api"

# Include routers
app.include_router(authRouter, prefix=PREFIX)
app.include_router(userRouter, prefix=PREFIX)
app.include_router(categoryRouter, prefix=PREFIX)
app.include_router(productRouter, prefix=PREFIX)
app.include_router(cartRouter, prefix=PREFIX)
app.include_router(orderRouter, prefix=PREFIX)
app.include_router(addressRouter, prefix=PREFIX)
app.include_router(checkoutRouter, prefix=PREFIX)
app.include_router(goshipRouter, prefix=PREFIX)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "E-Commerce API is running", "version": "1.0.0"}