import { useQueries } from "@tanstack/react-query";
import { ProductService } from "@/requests/product";

export interface CartItemDetail {
    id: string;
    productId: string;
    detailId: string;
    product_name: string;
    image: string;
    color: string;
    size: string;
    quantity: number;
    price: number;
}

interface CartItemRaw {
    id?: string;
    product_id?: string;
    productId?: string;
    detail_id?: string;
    productDetailId?: string;
    color?: string;
    size?: string;
    quantity: number;
    price?: number;
}

export const useCartItems = (cartItems?: CartItemRaw[]) => {
    const safeCartItems = cartItems || [];

    const productQueries = useQueries({
        queries: safeCartItems.map((item) => {
            const pid = item.product_id || item.productId || "";
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

        const pid = item.product_id || item.productId || "";
        const did = item.detail_id || item.productDetailId || "";

        // Tìm detail phù hợp từ product_details dựa trên detail_id
        const details = productData?.product_details || [];
        const matchedDetail = details.find(
            (d: any) => d.id === did
        );

        // Lấy image URL từ images array (mỗi image là object có url và thumbnail_url)
        const firstImage = productData?.images?.[0];
        const imageUrl = firstImage?.thumbnail_url || firstImage?.url || "";

        // Lấy color/size từ matched detail
        const color = item.color || matchedDetail?.color || "";
        const size = item.size || matchedDetail?.size || "";

        // Price: backend trả về dạng string, cần convert sang number
        const price = item.price || Number(productData?.price) || 0;

        return {
            id: item.id || `${pid}-${did}`,
            productId: pid,
            detailId: did,
            product_name: productData?.name || "",
            image: imageUrl,
            color,
            size,
            quantity: item.quantity,
            price,
        };
    });

    return {
        items,
        isLoading,
    };
};