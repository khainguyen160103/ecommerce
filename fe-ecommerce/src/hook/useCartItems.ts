import { useQueries } from "@tanstack/react-query";
import { ProductService } from "@/requests/product";
import { CartItemRaw } from "@/models/cart";

export interface CartItemDetail {
  id: string;
  product_id: string;
  detailId: string;
  product_name: string;
  image: string;
  color: string;
  size: string;
  quantity: number;
  price: number;
  /** Số lượng có trong kho (từ product_detail) */
  stock?: number;
}

export const useCartItems = (cartItems?: CartItemRaw[]) => {
  const safeCartItems = cartItems || [];

  const productQueries = useQueries({
    queries: safeCartItems.map((item) => {
      const pid = item.product_id || "";
      return {
        queryKey: ["product", pid],
        queryFn: () => ProductService.getById(pid),
        enabled: !!pid,
        staleTime: 60 * 60 * 1000,
      };
    }),
  });

  const isLoading = productQueries.some((query) => query.isLoading);

  const items: CartItemDetail[] = safeCartItems.map((item, index) => {
    const queryData = productQueries[index]?.data;
    // ProductService.getById returns Axios response, so .data is the product object
    const productData = queryData?.data || queryData;

    const pid = item.product_id || "";
    const did = item.detail_id || item.productDetailId || "";

    // Tìm detail phù hợp từ product_details dựa trên detail_id
    const details = productData?.product_details || [];
    const matchedDetail = details.find((d: any) => d.id === did);

    // Lấy image URL từ images array (mỗi image là object có url và thumbnail_url)
    const firstImage = productData?.images?.[0];
    const imageUrl = firstImage?.thumbnail_url || firstImage?.url || "";

    // Lấy color/size từ matched detail
    const color = item.color || matchedDetail?.color || "";
    const size = item.size || matchedDetail?.size || "";

    // Price: backend trả về dạng string, cần convert sang number
    const price = item.price || Number(productData?.price) || 0;

    // Stock từ product_detail (cùng phân loại)
    const stock = matchedDetail?.stock != null ? Number(matchedDetail.stock) : undefined;

    return {
      id: item.id || `${pid}-${did}`,
      product_id: pid,
      detailId: did,
      product_name: productData?.name || "",
      image: imageUrl,
      color,
      size,
      quantity: item.quantity,
      price,
      stock,
    };
  });

  return {
    items,
    isLoading,
  };
};