"""
VNPay Payment Gateway Utility
Hỗ trợ tạo URL thanh toán và xác thực kết quả từ VNPay
"""
import hashlib
import hmac
import urllib.parse
from datetime import datetime
from typing import Dict


class VNPayHelper:
    """Helper class for VNPay payment integration"""

    def __init__(self, tmn_code: str, hash_secret: str, payment_url: str, return_url: str):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.return_url = return_url

    def _hmac_sha512(self, key: str, data: str) -> str:
        """Generate HMAC SHA512 hash"""
        return hmac.new(
            key.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

    def create_payment_url(
        self,
        order_id: str,
        amount: int,
        order_info: str,
        ip_addr: str,
        bank_code: str = "",
    ) -> str:
        """
        Tạo URL thanh toán VNPay
        Args:
            order_id: Mã đơn hàng (vnp_TxnRef)
            amount: Số tiền (VND)
            order_info: Mô tả đơn hàng
            ip_addr: IP address của client
            bank_code: Mã ngân hàng (optional, để trống = chọn trên VNPay)
        Returns:
            URL để redirect user đến trang thanh toán VNPay
        """
        vnp_params: Dict[str, str] = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(amount * 100),  # VNPay yêu cầu amount * 100
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": ip_addr,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        if bank_code:
            vnp_params["vnp_BankCode"] = bank_code

        # Sort params alphabetically
        sorted_params = sorted(vnp_params.items())
        # VNPay yêu cầu dùng quote_plus (space -> +)
        query_string = "&".join(
            f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params
        )

        # Create HMAC SHA512 hash
        secure_hash = self._hmac_sha512(self.hash_secret, query_string)

        return f"{self.payment_url}?{query_string}&vnp_SecureHash={secure_hash}"

    def verify_response(self, params: Dict[str, str]) -> bool:
        """
        Xác thực response từ VNPay (return URL hoặc IPN)
        Args:
            params: Dict chứa tất cả query params từ VNPay
        Returns:
            True nếu hash hợp lệ
        """
        # Copy params để không ảnh hưởng original
        vnp_params = dict(params)
        vnp_secure_hash = vnp_params.pop("vnp_SecureHash", "")
        vnp_params.pop("vnp_SecureHashType", None)

        # Sort and encode (dùng quote_plus khớp với lúc tạo URL)
        sorted_params = sorted(vnp_params.items())
        query_string = "&".join(
            f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params
        )

        # Verify hash
        computed_hash = self._hmac_sha512(self.hash_secret, query_string)

        return computed_hash == vnp_secure_hash

    @staticmethod
    def is_payment_success(response_code: str) -> bool:
        """Kiểm tra mã response có phải thanh toán thành công không"""
        return response_code == "00"
