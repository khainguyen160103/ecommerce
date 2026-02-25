"""
Checkout Service - Xử lý logic thanh toán
Tích hợp VNPay QR và GoShip
"""
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.payment_detail_model import PaymentDetail
from app.models.user_model import User
from app.enum.role_enum import OrderStatus, PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.address_repository import AddressRepository
from app.utils.vnpay import VNPayHelper
from app.core.settings import settings
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, Annotated


class CheckoutService:
    """Service xử lý thanh toán"""

    def __init__(
        self,
        order_repo: Annotated[OrderRepository, Depends()],
        address_repo: Annotated[AddressRepository, Depends()],
    ):
        self.order_repo = order_repo
        self.address_repo = address_repo

    def _get_vnpay_helper(self) -> VNPayHelper:
        """Tạo VNPay helper instance"""
        return VNPayHelper(
            tmn_code=settings.VNPAY_TMN_CODE,
            hash_secret=settings.VNPAY_HASH_SECRET,
            payment_url=settings.VNPAY_PAYMENT_URL,
            return_url=settings.VNPAY_RETURN_URL,
        )

    def get_order_preview(self, user: User, session: Session) -> Dict[str, Any]:
        """
        Xem trước đơn hàng từ giỏ hàng
        """
        # Lấy giỏ hàng
        cart = self.order_repo.get_cart_by_user_id(user.id, session)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống",
            )

        cart_items = self.order_repo.get_cart_items(cart.id, session)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống",
            )

        # Lấy thông tin sản phẩm
        items = []
        subtotal = 0
        for item in cart_items:
            product = self.order_repo.get_product_by_id(item.product_id, session)
            if product and product.price:
                price = float(product.price)
                item_total = price * item.quantity
                subtotal += item_total
                items.append(
                    {
                        "id": str(item.id),
                        "product_id": str(item.product_id),
                        "detail_id": str(item.detail_id),
                        "product_name": product.name,
                        "price": price,
                        "quantity": item.quantity,
                        "item_total": item_total,
                    }
                )

        # Lấy địa chỉ
        address = None
        addresses = self.address_repo.get_addresses_by_user_id(user.id, session)
        if addresses:
            addr = addresses[0]
            address = {
                "id": str(addr.id),
                "title": addr.title,
                "address": addr.address,
                "phone_number": addr.phone_number,
            }

        return {
            "items": items,
            "subtotal": subtotal,
            "shipping_fee": 0,
            "total": subtotal,
            "address": address,
            "items_count": len(items),
        }

    def create_checkout(
        self,
        user: User,
        session: Session,
        payment_method: str,
        address_id: str | None,
        shipping_method: str,
        note: str,
        client_ip: str,
        rate_id: str | None = None,
        shipping_fee: int = 0,
    ) -> Dict[str, Any]:
        """
        Tạo đơn hàng và xử lý thanh toán
        """
        if payment_method not in ("vnpay", "cod"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phương thức thanh toán không hợp lệ. Chọn 'vnpay' hoặc 'cod'",
            )

        # Lấy giỏ hàng
        cart = self.order_repo.get_cart_by_user_id(user.id, session)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống",
            )

        cart_items = self.order_repo.get_cart_items(cart.id, session)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống",
            )

        # Tính tổng tiền
        total = 0
        for item in cart_items:
            product = self.order_repo.get_product_by_id(item.product_id, session)
            if product and product.price:
                total += float(product.price) * item.quantity

        total = int(total)
        total_with_shipping = total + shipping_fee

        # Tạo PaymentDetail
        payment = PaymentDetail(
            amount=total_with_shipping,
            provider=payment_method,
            status=PaymentStatus.PENDING,
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)

        # Tạo Order
        order = Order(
            user_id=user.id,
            total=total_with_shipping,
            status=OrderStatus.PENDING,
            payment_id=payment.id,
            shipping_fee=shipping_fee,
            rate_id=rate_id,
        )
        order = self.order_repo.create_order(order, session)

        # Tạo Order Items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )
            self.order_repo.create_order_item(order_item, session)

        self.order_repo.bulk_commit(session)

        # Xử lý theo phương thức thanh toán
        if payment_method == "vnpay":
            # VNPay: KHÔNG xóa giỏ hàng, chờ thanh toán thành công mới xóa
            vnpay = self._get_vnpay_helper()
            payment_url = vnpay.create_payment_url(
                order_id=str(order.id),
                amount=total_with_shipping,
                order_info=f"Thanh toan don hang {str(order.id)[:8]}",
                ip_addr=client_ip,
            )

            return {
                "message": "Đơn hàng đã được tạo. Vui lòng thanh toán qua VNPay.",
                "order_id": str(order.id),
                "payment_method": "vnpay",
                "payment_url": payment_url,
                "total": total_with_shipping,
            }
        else:
            # COD: xóa giỏ hàng ngay
            self._clear_cart(cart, cart_items, session)

            order.status = OrderStatus.CONFIRMED
            session.add(order)
            payment.status = PaymentStatus.PENDING
            session.add(payment)
            session.commit()

            return {
                "message": "Đặt hàng thành công! Thanh toán khi nhận hàng.",
                "order_id": str(order.id),
                "payment_method": "cod",
                "total": total_with_shipping,
                "total": total,
            }

    def _clear_cart(self, cart, cart_items, session: Session) -> None:
        """Xóa toàn bộ items trong giỏ hàng"""
        for item in cart_items:
            self.order_repo.delete_cart_item(item, session)
        cart.total = 0
        self.order_repo.update_cart_total(cart, session)

    def process_vnpay_return(
        self, params: Dict[str, str], session: Session
    ) -> Dict[str, Any]:
        """
        Xử lý kết quả thanh toán từ VNPay return URL
        """
        vnpay = self._get_vnpay_helper()

        # Verify hash
        is_valid = vnpay.verify_response(params)

        vnp_response_code = params.get("vnp_ResponseCode", "")
        vnp_txn_ref = params.get("vnp_TxnRef", "")
        vnp_amount = params.get("vnp_Amount", "0")
        vnp_transaction_no = params.get("vnp_TransactionNo", "")
        vnp_bank_code = params.get("vnp_BankCode", "")

        if not vnp_txn_ref:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin đơn hàng",
            }

        # Tìm order
        try:
            order_id = UUID(vnp_txn_ref)
        except ValueError:
            return {
                "success": False,
                "message": "Mã đơn hàng không hợp lệ",
            }

        order = self.order_repo.get_order_by_id(order_id, session)
        if not order:
            return {
                "success": False,
                "message": "Không tìm thấy đơn hàng",
            }

        if is_valid and VNPayHelper.is_payment_success(vnp_response_code):
            # Thanh toán thành công
            order.status = OrderStatus.CONFIRMED
            session.add(order)

            # Cập nhật payment
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.PAID
                    session.add(payment)

            # Xóa giỏ hàng sau khi thanh toán VNPay thành công
            cart = self.order_repo.get_cart_by_user_id(order.user_id, session)
            if cart:
                cart_items = self.order_repo.get_cart_items(cart.id, session)
                if cart_items:
                    self._clear_cart(cart, cart_items, session)

            session.commit()

            return {
                "success": True,
                "message": "Thanh toán thành công!",
                "order_id": str(order.id),
                "amount": int(vnp_amount) // 100,
                "transaction_no": vnp_transaction_no,
                "bank_code": vnp_bank_code,
            }
        else:
            # Thanh toán thất bại - KHÔNG xóa giỏ hàng để user thử lại
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.FAILED
                    session.add(payment)

            session.commit()

            return {
                "success": False,
                "message": "Thanh toán thất bại",
                "order_id": str(order.id),
                "response_code": vnp_response_code,
            }

    def process_vnpay_ipn(
        self, params: Dict[str, str], session: Session
    ) -> Dict[str, str]:
        """
        Xử lý VNPay IPN (server-to-server callback)
        """
        vnpay = self._get_vnpay_helper()
        is_valid = vnpay.verify_response(params)

        if not is_valid:
            return {"RspCode": "97", "Message": "Invalid Checksum"}

        vnp_txn_ref = params.get("vnp_TxnRef", "")
        vnp_response_code = params.get("vnp_ResponseCode", "")
        vnp_amount = params.get("vnp_Amount", "0")

        try:
            order_id = UUID(vnp_txn_ref)
        except ValueError:
            return {"RspCode": "01", "Message": "Order not found"}

        order = self.order_repo.get_order_by_id(order_id, session)
        if not order:
            return {"RspCode": "01", "Message": "Order not found"}

        # Check amount
        expected_amount = order.total * 100
        if int(vnp_amount) != expected_amount:
            return {"RspCode": "04", "Message": "Invalid amount"}

        # Check if already processed
        if order.status != OrderStatus.PENDING:
            return {"RspCode": "02", "Message": "Order already confirmed"}

        if VNPayHelper.is_payment_success(vnp_response_code):
            order.status = OrderStatus.CONFIRMED
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.PAID
                    session.add(payment)

            # Xóa giỏ hàng sau khi IPN xác nhận thành công
            cart = self.order_repo.get_cart_by_user_id(order.user_id, session)
            if cart:
                cart_items = self.order_repo.get_cart_items(cart.id, session)
                if cart_items:
                    self._clear_cart(cart, cart_items, session)
        else:
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.FAILED
                    session.add(payment)

        session.add(order)
        session.commit()

        return {"RspCode": "00", "Message": "Confirm Success"}

    def get_shipping_rates(
        self,
        user: User,
        session: Session,
        address_id: str,
        weight: float,
    ) -> Dict[str, Any]:
        """
        Tính phí vận chuyển qua GoShip API
        Lấy city/district từ địa chỉ user, tính rates thực tế
        """
        from app.utils.goship import goship_client
        from app.core.settings import settings

        # Lấy địa chỉ người nhận
        addresses = self.address_repo.get_addresses_by_user_id(user.id, session)
        if not addresses:
            # Trả về rates mẫu nếu chưa có địa chỉ
            return self._fallback_rates()

        addr = addresses[0]
        if not addr.city_id or not addr.district_id:
            return self._fallback_rates()

        try:
            rates = goship_client.get_rates(
                from_city=settings.GOSHIP_FROM_CITY,
                from_district=settings.GOSHIP_FROM_DISTRICT,
                to_city=addr.city_id,
                to_district=addr.district_id,
                cod=0,
                amount=0,
                weight=int(weight),
            )

            # Format kết quả
            formatted_rates = []
            for rate in rates:
                formatted_rates.append({
                    "id": str(rate.get("id", "")),
                    "name": rate.get("carrier_name", rate.get("name", "Giao hàng")),
                    "carrier": rate.get("carrier_short_name", rate.get("carrier", "GoShip")),
                    "carrier_logo": rate.get("carrier_logo", ""),
                    "estimated_days": rate.get("expected", rate.get("estimated_days", "3-5 ngày")),
                    "fee": int(rate.get("total_fee", rate.get("fee", 0))),
                })

            if not formatted_rates:
                return self._fallback_rates()

            return {"rates": formatted_rates}

        except Exception:
            return self._fallback_rates()

    def _fallback_rates(self) -> Dict[str, Any]:
        """Rates mẫu khi không gọi được GoShip"""
        return {
            "rates": [
                {
                    "id": "standard",
                    "name": "Giao hàng tiêu chuẩn",
                    "carrier": "GoShip",
                    "carrier_logo": "",
                    "estimated_days": "3-5 ngày",
                    "fee": 30000,
                },
                {
                    "id": "express",
                    "name": "Giao hàng nhanh",
                    "carrier": "GoShip Express",
                    "carrier_logo": "",
                    "estimated_days": "1-2 ngày",
                    "fee": 50000,
                },
            ]
        }
