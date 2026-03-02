"""
Report Repository - Xử lý queries cho báo cáo
"""
from sqlmodel import Session, select, and_
from sqlalchemy import func
from datetime import datetime, date
from typing import Dict, Any, List
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.enum.role_enum import OrderStatus


class ReportRepository:
    """Repository cho báo cáo doanh thu"""
    
    def get_revenue_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        session: Session
    ) -> Dict[str, Any]:
        """
        Báo cáo doanh thu theo khoảng thời gian
        Chỉ tính các đơn hàng đã CONFIRMED trở lên
        """
        query = select(
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total).label("total_revenue"),
            func.avg(Order.total).label("avg_order_value"),
        ).where(
            and_(
                Order.create_at >= start_date,
                Order.create_at < datetime.combine(end_date, datetime.max.time()),
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.SHIPPING,
                    OrderStatus.DELIVERED
                ])
            )
        )
        
        result = session.exec(query).first()
        
        return {
            "total_orders": result.total_orders or 0,
            "total_revenue": int(result.total_revenue or 0),
            "avg_order_value": int(result.avg_order_value or 0),
        }
    
    def get_revenue_by_day(
        self, 
        year: int, 
        month: int, 
        session: Session
    ) -> List[Dict[str, Any]]:
        """Báo cáo doanh thu theo từng ngày trong tháng"""
        query = select(
            func.date(Order.create_at).label("date"),
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total).label("revenue"),
        ).where(
            and_(
                func.year(Order.create_at) == year,
                func.month(Order.create_at) == month,
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.SHIPPING,
                    OrderStatus.DELIVERED
                ])
            )
        ).group_by(
            func.date(Order.create_at)
        ).order_by(
            func.date(Order.create_at)
        )
        
        results = session.exec(query).all()
        
        return [
            {
                "date": str(row.date),
                "total_orders": row.total_orders,
                "revenue": int(row.revenue or 0),
            }
            for row in results
        ]
    
    def get_revenue_by_month(
        self, 
        year: int, 
        session: Session
    ) -> List[Dict[str, Any]]:
        """Báo cáo doanh thu theo từng tháng trong năm"""
        query = select(
            func.month(Order.create_at).label("month"),
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total).label("revenue"),
        ).where(
            and_(
                func.year(Order.create_at) == year,
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.SHIPPING,
                    OrderStatus.DELIVERED
                ])
            )
        ).group_by(
            func.month(Order.create_at)
        ).order_by(
            func.month(Order.create_at)
        )
        
        results = session.exec(query).all()
        
        return [
            {
                "month": row.month,
                "total_orders": row.total_orders,
                "revenue": int(row.revenue or 0),
            }
            for row in results
        ]
    
    def get_top_selling_products(
        self,
        start_date: date,
        end_date: date,
        limit: int,
        session: Session
    ) -> List[Dict[str, Any]]:
        """Sản phẩm bán chạy nhất"""
        from app.models.product_model import Product
        
        query = select(
            OrderItem.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.count(OrderItem.id).label("total_orders"),
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Product, OrderItem.product_id == Product.id
        ).where(
            and_(
                Order.create_at >= start_date,
                Order.create_at < datetime.combine(end_date, datetime.max.time()),
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.SHIPPING,
                    OrderStatus.DELIVERED
                ])
            )
        ).group_by(
            OrderItem.product_id, Product.name
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(limit)
        
        results = session.exec(query).all()
        
        return [
            {
                "product_id": str(row.product_id),
                "product_name": row.name,
                "total_quantity": row.total_quantity,
                "total_orders": row.total_orders,
            }
            for row in results
        ]
    
    def get_order_status_summary(
        self,
        start_date: date,
        end_date: date,
        session: Session
    ) -> List[Dict[str, Any]]:
        """Thống kê đơn hàng theo trạng thái"""
        query = select(
            Order.status,
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total).label("total_value"),
        ).where(
            and_(
                Order.create_at >= start_date,
                Order.create_at < datetime.combine(end_date, datetime.max.time()),
            )
        ).group_by(
            Order.status
        )
        
        results = session.exec(query).all()
        
        return [
            {
                "status": row.status,
                "total_orders": row.total_orders,
                "total_value": int(row.total_value or 0),
            }
            for row in results
        ]
