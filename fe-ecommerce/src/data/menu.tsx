import { BarChart3, PackageSearch, ShoppingBasket, Truck, Users, Warehouse, TicketPercent } from "lucide-react";

export const menuItems = [
  {
    key: "orders",
    icon: <ShoppingBasket />,
    href: "/admin/order",
    label: "Quản lý đơn hàng",
  },
  {
    key: "category",
    icon: <Warehouse/>,
    label: "Quản lý loại mặt hàng",
    href: "/admin/category",
  },
  {
    key: "products",
    icon: <PackageSearch />,
    href: "/admin/product",
    label: "Quản lý sản phẩm",
  },
  {
    key: "discounts",
    icon: <TicketPercent />,
    href: "/admin/discount",
    label: "Quản lý mã giảm giá",
  },
  {
    key: "users",
    icon: <Users />,
    label: "Quản lý người dùng",
    href: "/admin/users",
  },
  {
    key: "delivery",
    icon: <Truck />,
    label: "Quản lý giao hàng",
    href: "/admin/delivery",
  },
  {
    key: "reports",
    icon: <BarChart3 />,
    label: "Báo cáo doanh thu",
    href: "/admin/reports",
  },
];
