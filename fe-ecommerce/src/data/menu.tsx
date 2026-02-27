import { PackageSearch, ShoppingBasket, Truck, Users, Warehouse } from "lucide-react";

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
];
