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
from app.repositories.discount_repository import DiscountRepository
from app.utils.vnpay import VNPayHelper
from app.core.settings import settings
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, Annotated, List, Optional


class CheckoutService:
    """Service xử lý thanh toán"""

    def __init__(
        self,
        order_repo: Annotated[OrderRepository, Depends()],
        address_repo: Annotated[AddressRepository, Depends()],
        discount_repo: Annotated[DiscountRepository, Depends()],
    ):
        self.order_repo = order_repo
        self.address_repo = address_repo
        self.discount_repo = discount_repo

    def _get_vnpay_helper(self) -> VNPayHelper:
        """Tạo VNPay helper instance"""
        return VNPayHelper(
            tmn_code=settings.VNPAY_TMN_CODE,
            hash_secret=settings.VNPAY_HASH_SECRET,
            payment_url=settings.VNPAY_PAYMENT_URL,
            return_url=settings.VNPAY_RETURN_URL,
        )

    def get_order_preview(
        self, user: User, session: Session, item_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Xem trước đơn hàng từ giỏ hàng
        item_ids: nếu có, chỉ lấy các cart items trong danh sách này
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

        # Lọc theo item_ids nếu có
        if item_ids:
            cart_items = [item for item in cart_items if str(item.id) in item_ids]
            if not cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không tìm thấy sản phẩm đã chọn trong giỏ hàng",
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
        item_ids: Optional[List[str]] = None,
        discount_code: str | None = None,
    ) -> Dict[str, Any]:
        """
        Tạo đơn hàng và xử lý thanh toán
        item_ids: nếu có, chỉ checkout các cart items trong danh sách này
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

        # Lọc theo item_ids nếu có
        if item_ids:
            cart_items = [item for item in cart_items if str(item.id) in item_ids]
            if not cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không tìm thấy sản phẩm đã chọn trong giỏ hàng",
                )

        # Tính tổng tiền
        total = 0
        for item in cart_items:
            product = self.order_repo.get_product_by_id(item.product_id, session)
            if product and product.price:
                total += float(product.price) * item.quantity

        total = int(total)

        # Áp dụng mã giảm giá
        discount_amount = 0
        applied_discount_code = None
        if discount_code:
            from app.services.discount_service import DiscountService

            discount_service = DiscountService(self.discount_repo)
            try:
                discount_result = discount_service.apply_discount(
                    discount_code, total, session
                )
                discount_amount = int(discount_result["discount_amount"])
                applied_discount_code = discount_result["code"]
            except HTTPException:
                # Nếu mã giảm giá không hợp lệ, bỏ qua và không áp dụng
                pass

        total_with_shipping = total + shipping_fee - discount_amount
        if total_with_shipping < 0:
            total_with_shipping = 0

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
            discount_code=applied_discount_code,
            discount_amount=discount_amount,
        )
        order = self.order_repo.create_order(order, session)

        # Tạo Order Items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                detail_id=cart_item.detail_id,  # Lưu detail_id để biết chi tiết sản phẩm
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
            # COD: xóa giỏ hàng ngay và giảm stock
            self._clear_cart(cart, cart_items, session)

            # Giảm stock cho từng product detail
            for cart_item in cart_items:
                success = self.order_repo.reduce_product_stock(
                    cart_item.detail_id, cart_item.quantity, session
                )
                if not success:
                    # Rollback nếu không đủ stock
                    session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Sản phẩm không đủ số lượng trong kho",
                    )

            order.status = OrderStatus.PENDING
            session.add(order)
            payment.status = PaymentStatus.PENDING
            session.add(payment)
            session.commit()

            # Tăng số lần sử dụng mã giảm giá
            if applied_discount_code:
                from app.services.discount_service import DiscountService

                discount_service = DiscountService(self.discount_repo)
                discount_service.use_discount(applied_discount_code, session)

            return {
                "message": "Đặt hàng thành công! Đơn hàng đang chờ xác nhận.",
                "order_id": str(order.id),
                "payment_method": "cod",
                "total": total_with_shipping,
            }

    def _clear_cart(self, cart, cart_items, session: Session) -> None:
        """Xóa các items đã checkout khỏi giỏ hàng"""
        for item in cart_items:
            self.order_repo.delete_cart_item(item, session)
        # Lấy lại remaining items để cập nhật total
        remaining = self.order_repo.get_cart_items(cart.id, session)
        if not remaining:
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
            # Thanh toán thành công - giữ trạng thái PENDING để admin xác nhận
            # order.status vẫn là PENDING (chờ xác nhận)
            session.add(order)

            # Cập nhật payment
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.PAID
                    session.add(payment)

            # Giảm stock cho các sản phẩm trong đơn hàng
            order_items = self.order_repo.get_order_items(order.id, session)
            for item in order_items:
                success = self.order_repo.reduce_product_stock(
                    item.detail_id, item.quantity, session
                )
                if not success:
                    # Log warning nhưng không rollback vì đã thanh toán
                    print(
                        f"[WARNING] Không đủ stock cho product_detail {item.detail_id}"
                    )

            # Xóa giỏ hàng sau khi thanh toán VNPay thành công
            cart = self.order_repo.get_cart_by_user_id(order.user_id, session)
            if cart:
                cart_items = self.order_repo.get_cart_items(cart.id, session)
                if cart_items:
                    self._clear_cart(cart, cart_items, session)

            # Tăng số lần sử dụng mã giảm giá
            if order.discount_code:
                from app.services.discount_service import DiscountService

                discount_service = DiscountService(self.discount_repo)
                discount_service.use_discount(order.discount_code, session)

            session.commit()

            return {
                "success": True,
                "message": "Thanh toán thành công! Đơn hàng đang chờ xác nhận.",
                "order_id": str(order.id),
                "amount": int(vnp_amount) // 100,
                "transaction_no": vnp_transaction_no,
                "bank_code": vnp_bank_code,
            }
        else:
            # Thanh toán thất bại - xóa đơn hàng và payment, không lưu lại
            payment_id = order.payment_id

            # Xóa order items trước
            self.order_repo.delete_order_items(order.id, session)
            # Xóa order
            self.order_repo.delete_order(order, session)
            # Xóa payment
            if payment_id:
                payment = session.get(PaymentDetail, payment_id)
                if payment:
                    session.delete(payment)

            session.commit()

            return {
                "success": False,
                "message": "Thanh toán thất bại. Đơn hàng không được lưu, bạn có thể quay lại giỏ hàng để đặt lại.",
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
            # Thanh toán thành công - giữ trạng thái PENDING để admin xác nhận
            if order.payment_id:
                payment = session.get(PaymentDetail, order.payment_id)
                if payment:
                    payment.status = PaymentStatus.PAID
                    session.add(payment)

            # Giảm stock cho các sản phẩm trong đơn hàng
            order_items = self.order_repo.get_order_items(order.id, session)
            for item in order_items:
                success = self.order_repo.reduce_product_stock(
                    item.detail_id, item.quantity, session
                )
                if not success:
                    print(
                        f"[WARNING] Không đủ stock cho product_detail {item.detail_id}"
                    )

            # Xóa giỏ hàng sau khi IPN xác nhận thành công
            cart = self.order_repo.get_cart_by_user_id(order.user_id, session)
            if cart:
                cart_items = self.order_repo.get_cart_items(cart.id, session)
                if cart_items:
                    self._clear_cart(cart, cart_items, session)

            session.add(order)
            session.commit()
        else:
            # Thanh toán thất bại qua IPN - xóa đơn hàng, không lưu lại
            payment_id = order.payment_id
            self.order_repo.delete_order_items(order.id, session)
            self.order_repo.delete_order(order, session)
            if payment_id:
                payment = session.get(PaymentDetail, payment_id)
                if payment:
                    session.delete(payment)
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
        import logging

        logger = logging.getLogger(__name__)

        # Lấy địa chỉ người nhận
        addresses = self.address_repo.get_addresses_by_user_id(user.id, session)
        if not addresses:
            logger.warning("User %s chưa có địa chỉ nào → dùng fallback rates", user.id)
            return self._fallback_rates(reason="Chưa có địa chỉ giao hàng")

        addr = addresses[0]

        # Validate địa chỉ có đủ thông tin
        if not addr.city_id or not addr.district_id:
            logger.warning(
                "Địa chỉ %s thiếu city_id hoặc district_id (city=%s, district=%s) → fallback",
                addr.id,
                addr.city_id,
                addr.district_id,
            )
            return self._fallback_rates(
                reason="Địa chỉ giao hàng chưa có thông tin tỉnh/quận đầy đủ"
            )

        # Validate cấu hình kho gửi hàng
        if not settings.GOSHIP_FROM_CITY or not settings.GOSHIP_FROM_DISTRICT:
            logger.error(
                "Thiếu cấu hình GOSHIP_FROM_CITY=%s hoặc GOSHIP_FROM_DISTRICT=%s → fallback",
                settings.GOSHIP_FROM_CITY,
                settings.GOSHIP_FROM_DISTRICT,
            )
            return self._fallback_rates(
                reason="Hệ thống chưa cấu hình địa chỉ kho gửi hàng"
            )

        try:
            logger.info(
                "Gọi GoShip rates: from_city=%s, from_district=%s, to_city=%s, to_district=%s",
                settings.GOSHIP_FROM_CITY,
                settings.GOSHIP_FROM_DISTRICT,
                addr.city_id,
                addr.district_id,
            )

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
                logger.warning("GoShip trả về danh sách rates rỗng → fallback")
                return self._fallback_rates(
                    reason="GoShip không có dịch vụ phù hợp cho tuyến này"
                )

            logger.info("GoShip rates thành công: %d rates", len(formatted_rates))
            return {"rates": formatted_rates, "source": "goship"}

        except Exception as e:
            logger.error("Lỗi gọi GoShip rates: %s → fallback", str(e), exc_info=True)
            return self._fallback_rates(reason=f"Lỗi kết nối GoShip: {str(e)}")

    def _fallback_rates(self, reason: str = "GoShip không khả dụng") -> Dict[str, Any]:
        """Rates mẫu khi không gọi được GoShip"""
        return {
            "rates": [
                {
                    "id": "standard_fallback",
                    "name": "Giao hàng tiêu chuẩn",
                    "carrier": "Nội bộ",
                    "carrier_logo": "",
                    "estimated_days": "3-5 ngày",
                    "fee": 30000,
                },
                {
                    "id": "express_fallback",
                    "name": "Giao hàng nhanh",
                    "carrier": "Nội bộ",
                    "carrier_logo": "",
                    "estimated_days": "1-2 ngày",
                    "fee": 50000,
                },
            ],
            "source": "fallback",
            "warning": reason,
            "note": "Đây là phí vận chuyển tạm tính. Để có phí chính xác từ GoShip, vui lòng đảm bảo địa chỉ giao hàng có đầy đủ thông tin tỉnh/quận/phường.",
        }
