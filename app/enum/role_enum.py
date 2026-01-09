"""
Role Enum - Định nghĩa các role trong hệ thống
"""
from enum import IntEnum

class RoleEnum(IntEnum):
    ADMIN = 0   # Quản trị viên - toàn quyền
    USER = 1    # Người dùng đã đăng ký
    


class OrderStatus:
    """Trạng thái đơn hàng"""
    PENDING = "pending"         # Chờ xác nhận
    CONFIRMED = "confirmed"     # Đã xác nhận
    SHIPPING = "shipping"       # Đang giao hàng
    DELIVERED = "delivered"     # Đã giao hàng
    CANCELLED = "cancelled"     # Đã hủy


class PaymentStatus:
    """Trạng thái thanh toán"""
    PENDING = "pending"         # Chờ thanh toán
    PAID = "paid"               # Đã thanh toán
    FAILED = "failed"           # Thanh toán thất bại
    REFUNDED = "refunded"       # Đã hoàn tiền