"""
Report Router - API endpoints cho báo cáo doanh thu (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import date
from typing import Annotated, Dict, Any
from app.core.database import get_session
from app.models.user_model import UserOut
from app.deps.auth_dependency import get_current_user
from app.services.report_service import ReportService

reportRouter = APIRouter(prefix="/reports", tags=["Reports - Báo cáo"])


def require_admin(current_user: Annotated[UserOut, Depends(get_current_user)]) -> UserOut:
    """Require admin role"""
    role = str(current_user.role or "").upper()
    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập báo cáo"
        )
    return current_user


@reportRouter.get("/dashboard", summary="[ADMIN] Dashboard tổng quan")
def get_dashboard(
    period: str = Query("month", description="today, week, month, year"),
    session: Annotated[Session, Depends(get_session)] = None,
    current_user: Annotated[UserOut, Depends(require_admin)] = None,
    service: Annotated[ReportService, Depends()] = None,
) -> Dict[str, Any]:
    """
    Dashboard tổng quan với doanh thu, top sản phẩm, thống kê đơn hàng
    """
    if period not in ["today", "week", "month", "year"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period phải là: today, week, month, hoặc year"
        )
    
    return service.get_dashboard_summary(session, period)


@reportRouter.get("/revenue/daily", summary="[ADMIN] Doanh thu theo ngày")
def get_daily_revenue(
    year: int = Query(..., description="Năm (VD: 2024)"),
    month: int = Query(..., ge=1, le=12, description="Tháng (1-12)"),
    session: Annotated[Session, Depends(get_session)] = None,
    current_user: Annotated[UserOut, Depends(require_admin)] = None,
    service: Annotated[ReportService, Depends()] = None,
) -> Dict[str, Any]:
    """
    Báo cáo doanh thu theo từng ngày trong tháng
    """
    return service.get_revenue_by_day(year, month, session)


@reportRouter.get("/revenue/monthly", summary="[ADMIN] Doanh thu theo tháng")
def get_monthly_revenue(
    year: int = Query(..., description="Năm (VD: 2024)"),
    session: Annotated[Session, Depends(get_session)] = None,
    current_user: Annotated[UserOut, Depends(require_admin)] = None,
    service: Annotated[ReportService, Depends()] = None,
) -> Dict[str, Any]:
    """
    Báo cáo doanh thu theo từng tháng trong năm
    """
    return service.get_revenue_by_month(year, session)


@reportRouter.get("/revenue/custom", summary="[ADMIN] Doanh thu tùy chỉnh")
def get_custom_revenue(
    start_date: date = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    session: Annotated[Session, Depends(get_session)] = None,
    current_user: Annotated[UserOut, Depends(require_admin)] = None,
    service: Annotated[ReportService, Depends()] = None,
) -> Dict[str, Any]:
    """
    Báo cáo doanh thu theo khoảng thời gian tùy chỉnh
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ngày bắt đầu phải nhỏ hơn ngày kết thúc"
        )
    
    return service.get_custom_report(start_date, end_date, session)
