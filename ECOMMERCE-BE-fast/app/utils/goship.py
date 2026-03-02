"""
GoShip API Client - Tích hợp dịch vụ vận chuyển GoShip
API v2: https://sandbox.goship.io/api/v2

IMPORTANT: GoShip yêu cầu login để lấy access token trước khi gọi API
- Auth endpoint: https://sandbox.goship.io/api/v2/login
- Body: username, password, client_id, client_secret
- API endpoints: https://sandbox.goship.io/api/v2/*

Location API: https://provinces.open-api.vn/api/ (fallback do GoShip sandbox không ổn định)

NOTE: GoShip sandbox có thể không ổn định, fallback mechanism đã được implement trong router
"""
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.settings import settings

logger = logging.getLogger(__name__)

PROVINCES_API = "https://provinces.open-api.vn/api"


class GoShipClient:
    """Client gọi GoShip API v2 + Vietnam Provinces API cho địa chỉ"""

    _access_token: Optional[str] = None
    _token_expires_at: Optional[datetime] = None
    _refresh_token: Optional[str] = None

    def __init__(self):
        self.base_url = settings.GOSHIP_API_URL
        self.username = settings.GOSHIP_USERNAME
        self.password = settings.GOSHIP_PASSWORD
        self.client_id = settings.GOSHIP_CLIENT_ID
        self.client_secret = settings.GOSHIP_CLIENT_SECRET

    # ==================== AUTH ====================

    def _get_token(self) -> str:
        """Lấy access token, tự động refresh nếu hết hạn"""
        now = datetime.now()
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return self._access_token

        if not self.username or not self.password:
            raise RuntimeError(
                "Thiếu cấu hình GoShip login: GOSHIP_USERNAME/GOSHIP_PASSWORD"
            )

        try:
            login_url = f"{self.base_url}/login"

            response = httpx.post(
                login_url,
                json={
                    "username": self.username,
                    "password": self.password,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=10,
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()

            self._access_token = data.get("access_token")
            self._refresh_token = data.get("refresh_token")
            if not self._access_token:
                raise RuntimeError("GoShip login không trả về access_token")

            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = now + timedelta(seconds=expires_in - 60)

            logger.info("GoShip login successful")
            return self._access_token
        except httpx.HTTPStatusError as e:
            logger.error(
                "GoShip login failed: %s - %s", e.response.status_code, e.response.text
            )
            raise RuntimeError(f"GoShip login failed: {e.response.status_code}") from e
        except Exception as e:
            logger.error("GoShip login failed: %s", str(e))
            raise RuntimeError(f"GoShip không khả dụng: {e}") from e

    def _headers(self) -> Dict[str, str]:
        """Headers với Bearer token"""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ==================== LOCATIONS (provinces.open-api.vn) ====================

    def get_cities(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tỉnh/thành phố từ Vietnam Provinces API"""
        response = httpx.get(
            f"{PROVINCES_API}/",
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
        # Chuẩn hóa: {id, name} format
        return [{"id": p["code"], "name": p["name"]} for p in data]

    def get_districts(self, city_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách quận/huyện theo tỉnh/thành"""
        response = httpx.get(
            f"{PROVINCES_API}/p/{city_id}?depth=2",
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
        districts = data.get("districts", [])
        return [{"id": d["code"], "name": d["name"]} for d in districts]

    def get_wards(self, district_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách phường/xã theo quận/huyện"""
        response = httpx.get(
            f"{PROVINCES_API}/d/{district_id}?depth=2",
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()
        wards = data.get("wards", [])
        return [{"id": w["code"], "name": w["name"]} for w in wards]

    # ==================== RATES ====================

    def get_rates(
        self,
        from_city: int,
        from_district: int,
        to_city: int,
        to_district: int,
        cod: int = 0,
        amount: int = 0,
        weight: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Tính phí vận chuyển từ các đơn vị vận chuyển
        Args:
            from_city: ID thành phố gửi
            from_district: ID quận gửi
            to_city: ID thành phố nhận
            to_district: ID quận nhận
            cod: Tiền thu hộ (VND)
            amount: Giá trị hàng hóa (VND)
            weight: Trọng lượng (gram)
        Returns:
            List các rate từ nhiều đơn vị vận chuyển
        """
        response = httpx.post(
            f"{self.base_url}/rates",
            headers=self._headers(),
            json={
                "shipment": {
                    "address_from": {
                        "city": from_city,
                        "district": from_district,
                    },
                    "address_to": {
                        "city": to_city,
                        "district": to_district,
                    },
                    "parcel": {
                        "cod": cod,
                        "amount": amount,
                        "weight": weight,
                    },
                }
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    # ==================== SHIPMENTS ====================

    def create_shipment(
        self,
        rate_id: str,
        order_id: str,
        payer: int,
        from_name: str,
        from_phone: str,
        from_street: str,
        from_ward: str,
        from_district: str,
        from_city: str,
        to_name: str,
        to_phone: str,
        to_street: str,
        to_ward: str,
        to_district: str,
        to_city: str,
        cod: int = 0,
        amount: int = 0,
        weight: str = "500",
        width: str = "15",
        height: str = "15",
        length: str = "15",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Tạo đơn vận chuyển trên GoShip
        Args:
            rate_id: ID của rate đã chọn (từ get_rates)
            order_id: Mã đơn hàng
            payer: 0 = người nhận trả phí, 1 = người gửi trả phí
            from/to: Thông tin địa chỉ gửi/nhận
            cod: Tiền thu hộ (VND)
            amount: Giá trị hàng hóa (VND)
            weight/width/height/length: Thông tin kiện hàng (string)
            metadata: Ghi chú kiện hàng
        Returns:
            Thông tin shipment (id, tracking_number, ...)
        """
        payload = {
            "shipment": {
                "rate": rate_id,
                "payer": payer,
                "order_id": order_id,
                "address_from": {
                    "name": from_name,
                    "phone": from_phone,
                    "street": from_street,
                    "ward": str(from_ward),
                    "district": str(from_district),
                    "city": str(from_city),
                },
                "address_to": {
                    "name": to_name,
                    "phone": to_phone,
                    "street": to_street,
                    "ward": str(to_ward),
                    "district": str(to_district),
                    "city": str(to_city),
                },
                "parcel": {
                    "cod": cod,
                    "amount": amount,
                    "weight": str(weight),
                    "width": str(width),
                    "height": str(height),
                    "length": str(length),
                    "metadata": metadata,
                },
            }
        }
        logger.info("GoShip create_shipment payload: %s", payload)
        print(f"[GoShip] Creating shipment with payload: {payload}")

        response = httpx.post(
            f"{self.base_url}/shipments",
            headers=self._headers(),
            json=payload,
            timeout=30,
            follow_redirects=True,
        )

        # Log response chi tiết để debug
        print(f"[GoShip] Response status: {response.status_code}")
        print(f"[GoShip] Response body: {response.text}")

        if response.status_code >= 400:
            logger.error(
                "GoShip create_shipment failed: %s - %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError(
                f"GoShip API error {response.status_code}: {response.text}"
            )

        data = response.json()
        payload = data.get("data", data) if isinstance(data, dict) else data

        # GoShip tạo vận đơn theo cơ chế async: HTTP 200 OK nhưng có thể có lỗi nghiệp vụ
        # Theo tài liệu: shipment_status = 900 là "Đơn mới" (bình thường)
        # CHỈ KHI có carrier_error thì mới là lỗi thực sự
        if isinstance(payload, dict):
            carrier_error = payload.get("carrier_error")
            if carrier_error:
                raise RuntimeError(f"GoShip carrier error: {carrier_error}")

        return payload

    def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết + tracking của đơn vận chuyển"""
        response = httpx.get(
            f"{self.base_url}/shipments/{shipment_id}",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def cancel_shipment(self, shipment_id: str) -> Dict[str, Any]:
        """Hủy đơn vận chuyển theo tài liệu GoShip (DELETE /shipments/{id})"""
        response = httpx.delete(
            f"{self.base_url}/shipments/{shipment_id}",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data


# Singleton instance
goship_client = GoShipClient()
