"""
GoShip API Client - Tích hợp dịch vụ vận chuyển GoShip
API v2: https://sandbox.goship.io/api/v2
Location API: https://provinces.open-api.vn/api/ (fallback do GoShip sandbox không ổn định)
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.settings import settings


PROVINCES_API = "https://provinces.open-api.vn/api"


class GoShipClient:
    """Client gọi GoShip API v2 + Vietnam Provinces API cho địa chỉ"""

    _access_token: Optional[str] = None
    _token_expires_at: Optional[datetime] = None

    def __init__(self):
        self.base_url = settings.GOSHIP_API_URL
        self.client_id = settings.GOSHIP_CLIENT_ID
        self.client_secret = settings.GOSHIP_CLIENT_SECRET

    # ==================== AUTH ====================

    def _get_token(self) -> str:
        """Lấy access token, tự động refresh nếu hết hạn"""
        now = datetime.now()
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return self._access_token

        response = httpx.post(
            f"{self.base_url}/login",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=5,
            follow_redirects=True,
        )
        response.raise_for_status()
        data = response.json()

        self._access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = now + timedelta(seconds=expires_in - 60)

        return self._access_token

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
        from_name: str,
        from_phone: str,
        from_street: str,
        from_ward: int,
        from_district: int,
        from_city: int,
        to_name: str,
        to_phone: str,
        to_street: str,
        to_ward: int,
        to_district: int,
        to_city: int,
        cod: int = 0,
        weight: int = 500,
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Tạo đơn vận chuyển trên GoShip
        Args:
            rate_id: ID của rate đã chọn (từ get_rates)
            from/to: Thông tin địa chỉ gửi/nhận
        Returns:
            Thông tin shipment (id, tracking_number, ...)
        """
        response = httpx.post(
            f"{self.base_url}/shipments",
            headers=self._headers(),
            json={
                "shipment": {
                    "rate": rate_id,
                    "address_from": {
                        "name": from_name,
                        "phone": from_phone,
                        "street": from_street,
                        "ward": from_ward,
                        "district": from_district,
                        "city": from_city,
                    },
                    "address_to": {
                        "name": to_name,
                        "phone": to_phone,
                        "street": to_street,
                        "ward": to_ward,
                        "district": to_district,
                        "city": to_city,
                    },
                    "parcel": {
                        "cod": cod,
                        "weight": weight,
                        "metadata": metadata,
                    },
                }
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

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
        """Hủy đơn vận chuyển"""
        response = httpx.patch(
            f"{self.base_url}/shipments/{shipment_id}/cancel",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data


# Singleton instance
goship_client = GoShipClient()
