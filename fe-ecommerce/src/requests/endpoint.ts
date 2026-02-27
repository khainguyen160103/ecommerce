export const ENDPOINT = { 
    AUTH : { 
        LOGIN : 'auth/token',
        ME : 'auth/me', 
        REGISTER: 'auth/register', 
        LOGOUT: 'auth/logout',
        GOOGLE: 'auth/google',
        FACEBOOK: 'auth/facebook',
        CHANGE_PASSWORD: 'auth/change-password'
    },
    USER : { 
        GETALL : 'users',
        GET_BY_ID : (id) => `users/${id}`, 
        DELETE: (id) => `users${id}`, 
        CREATE: "users", 
        UPDATE: (id) => `users/${id}`
    },
    PRODUCT: { 
        GETALL: 'products', 
        CREATE: 'products',
        SEARCH: 'products/search',
        GET_BY_ID: (id) => `products/${id}`, 
        DELETE: (id) => `products/${id}`, 
        UPDATE: (id) => `products/${id}`, 
        GET_PRODUCT_DETAIL: (id) => `products/${id}/details`,   
        ADD_PRODUCT_DETAIL: (id) => `products/${id}/details`,
        DELETE_PRODUCT_DETAIL: (id) => `products/${id}/details`,     
    },
    CATEGORY: { 
        CREATE: 'categories', 
        DELETE: (id) => `categories/${id}`,
        GET_ALL: 'categories',
        UPDATE: (id) => `categories/${id}`, 
        GET_BY_ID: (id) => `categories/${id}`
    },
    CART: {
        GET_MY_CART: 'cart/',
        ADD_ITEM: 'cart/items',
        UPDATE_ITEM: (itemId) => `cart/items/${itemId}`,
        DELETE_ITEM: (itemId) => `cart/items/${itemId}`,
        CLEAR_CART: 'cart/'
    },
    ORDER: {
        GET_MY_ORDERS: 'orders/my-orders',
        GET_MY_ORDER_BY_ID: (id) => `orders/my-orders/${id}`,
        CREATE_ORDER: 'orders/',
        CANCEL_ORDER: (id) => `orders/my-orders/${id}/cancel`,
        GET_ALL_ORDERS: 'orders/',
        GET_ORDER_BY_ID: (id) => `orders/${id}`,
        UPDATE_ORDER_STATUS: (id) => `orders/${id}/status`
    },
    ADDRESS: {
        GET_MY_ADDRESSES: 'addresses/',
        GET_BY_ID: (id) => `addresses/${id}`,
        CREATE: 'addresses/',
        UPDATE: (id) => `addresses/${id}`,
        DELETE: (id) => `addresses/${id}`
    },
    CHECKOUT: {
        CREATE: 'checkout/',
        ORDER_PREVIEW: 'checkout/order-preview',
        VNPAY_RETURN: 'checkout/vnpay-return',
        SHIPPING_RATES: 'checkout/shipping-rates'
    },
    GOSHIP: {
        CITIES: 'goship/cities',
        DISTRICTS: (cityId) => `goship/cities/${cityId}/districts`,
        WARDS: (districtId) => `goship/districts/${districtId}/wards`,
        RATES: 'goship/rates',
        CREATE_SHIPMENT: 'goship/shipments',
        TRACKING: (orderId) => `goship/shipments/${orderId}/tracking`,
        CANCEL_SHIPMENT: (orderId) => `goship/shipments/${orderId}/cancel`
    }
}