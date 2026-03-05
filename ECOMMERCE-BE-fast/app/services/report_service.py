"""
Report Service - Xử lý logic báo cáo doanh thu
"""
from typing import Annotated, Dict, Any, List
from datetime import datetime, date, timedelta, timezone
from fastapi import Depends
from sqlmodel import Session
from app.repositories.report_repository import ReportRepository

VN_TZ = timezone(timedelta(hours=7))


class ReportService:
    """Service xử lý báo cáo"""
    
    def __init__(self, repo: Annotated[ReportRepository, Depends()]):
        self.repo = repo
    
    def get_dashboard_summary(
        self,
        session: Session,
        period: str = "month"  # today, week, month, year
    ) -> Dict[str, Any]:
        """Tổng quan dashboard cho admin"""
        today = datetime.now(VN_TZ).date()
        
        if period == "today":
            start_date = today
            end_date = today
        elif period == "week":
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == "month":
            start_date = today.replace(day=1)
            end_date = today
        else:  # year
            start_date = today.replace(month=1, day=1)
            end_date = today
        
        # Doanh thu tổng
        revenue_data = self.repo.get_revenue_by_date_range(
            start_date, end_date, session
        )
        
        # Top sản phẩm
        top_products = self.repo.get_top_selling_products(
            start_date, end_date, 5, session
        )
        
        # Thống kê trạng thái đơn hàng
        status_summary = self.repo.get_order_status_summary(
            start_date, end_date, session
        )
        
        return {
            "period": period,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "revenue": revenue_data,
            "top_products": top_products,
            "status_summary": status_summary,
        }
    
    def get_revenue_by_day(
        self,
        year: int,
        month: int,
        session: Session
    ) -> Dict[str, Any]:
        """Báo cáo doanh thu theo ngày"""
        daily_data = self.repo.get_revenue_by_day(year, month, session)
        
        # Tính tổng
        total_revenue = sum(item["revenue"] for item in daily_data)
        total_orders = sum(item["total_orders"] for item in daily_data)
        
        return {
            "year": year,
            "month": month,
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "daily_data": daily_data,
        }
    
    def get_revenue_by_month(
        self,
        year: int,
        session: Session
    ) -> Dict[str, Any]:
        """Báo cáo doanh thu theo tháng"""
        monthly_data = self.repo.get_revenue_by_month(year, session)
        
        # Tính tổng
        total_revenue = sum(item["revenue"] for item in monthly_data)
        total_orders = sum(item["total_orders"] for item in monthly_data)
        
        return {
            "year": year,
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "monthly_data": monthly_data,
        }
    
    def get_custom_report(
        self,
        start_date: date,
        end_date: date,
        session: Session
    ) -> Dict[str, Any]:
        """Báo cáo theo khoảng thời gian tùy chỉnh"""
        revenue_data = self.repo.get_revenue_by_date_range(
            start_date, end_date, session
        )
        
        top_products = self.repo.get_top_selling_products(
            start_date, end_date, 10, session
        )
        
        status_summary = self.repo.get_order_status_summary(
            start_date, end_date, session
        )
        
        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "revenue": revenue_data,
            "top_products": top_products,
            "status_summary": status_summary,
        }
