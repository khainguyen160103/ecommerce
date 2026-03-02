"""
Timezone helper - Hỗ trợ múi giờ Việt Nam (UTC+7)
"""
from datetime import datetime, timezone, timedelta

VN_TIMEZONE = timezone(timedelta(hours=7))


def vn_now() -> datetime:
    """Trả về thời gian hiện tại theo múi giờ Việt Nam (UTC+7)"""
    return datetime.now(VN_TIMEZONE)
