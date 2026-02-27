'use client'
import Image from "next/image";
import Link from "next/link";
import Spinner from "@/components/Spinner";
import HeaderTop from "@/components/Header";
import { Card, Row, Col, Pagination, Tag } from "antd";
import { useState } from "react";
import { useProduct } from "@/hook/useProduct";
import { useCategory } from "@/hook/useCategory";
import { Product } from "@/types/product";
import { Truck } from "lucide-react";
import _ from "lodash";
import { ProductService } from "@/requests/product";
import { useSearch } from "@/hook/useSearch";
export default function Home() {
  const { keyword, isSearching, searchQuery, clearSearch } = useSearch()
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  
  const { productsData, queryClient } = useProduct();
  const { categoriesData } = useCategory();
  const {data: products , pagination} = productsData.data || {}
  const {data: categories} = categoriesData.data || {}
  
  // Nếu đang search → dùng kết quả từ API search, ngược lại dùng danh sách thường
  const searchResults: Product[] = searchQuery?.data?.data || [];
  const allProducts: Product[] = products || [];
  
  const displayProducts = isSearching ? searchResults : allProducts.filter(product => {
    const matchCategory = !selectedCategory || product.category_id === selectedCategory;
    return matchCategory;
  });

  const isLoading = isSearching ? searchQuery.isLoading : productsData.isLoading;

  const categoryOptions = categories?.map((cat: any) => ({
    label: cat.name,
    value: cat.id
  })) || [];

  const handleCategoryChange = (value: string | undefined) => {
    setSelectedCategory(value);
    setCurrentPage(1);
  };

  const handlePaginationChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleHoverProduct = _.debounce((id: string)=> { 
    queryClient.prefetchQuery({ 
      queryKey: ['product' , id] , 
      queryFn: () => ProductService.getById(id)
    })
  }, 300)

  // filteredProducts.map(products => { 
  //   products.images.map((image: any) => { 
  //     console.log(image.url)
  //   })
  // })
  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        {/* Hero Banner removed */}

        <div className="max-w-7xl mx-auto px-4 py-8 sm:py-12">
          {/* Search Indicator */}
          {isSearching && (
            <div className="flex items-center gap-2 mb-6">
              <span className="text-gray-600">
                Kết quả tìm kiếm cho: <strong>&quot;{keyword}&quot;</strong>
                {!searchQuery.isLoading && ` (${displayProducts.length} sản phẩm)`}
              </span>
              <Tag
                closable
                onClose={clearSearch}
                color="blue"
                className="cursor-pointer"
              >
                Xóa bộ lọc
              </Tag>
            </div>
          )}

          {/* Products Grid */}
          {isLoading ? <Spinner /> : 

          (displayProducts.length > 0 ? (
            <>
              <Row gutter={[16, 24]}>
                {displayProducts.map((product) => (
                  <Col key={product.id} xs={24} sm={12} md={8} lg={6}> 
                    <Link href={`/product/${product.id}`}>
                      <Card
                        onMouseEnter={() => handleHoverProduct(product.id)}
                        hoverable
                        className="h-full shadow-md hover:shadow-xl transition-shadow duration-300 rounded-xl overflow-hidden"
                        cover={
                          <div className="w-full h-56 bg-gray-100 flex items-center justify-center overflow-hidden relative group">
                            <Image
                              src={product.images[0].url}
                              alt={product.name}
                              fill
                              className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-300"
                              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                            />
                          </div>
                        }
                      >
                        <div className="flex flex-col h-full gap-3">
                          <h3 className="font-sans text-base text-gray-800 line-clamp-2">
                            {product.name}
                          </h3>
                          
                          <div className="flex items-end justify-between pt-2">
                            <span className="text-xl font-sans text-red-500">
                              {parseFloat(product.price).toLocaleString('vi-VN')} ₫
                            </span>
                            <Truck strokeWidth={1.5} size={24} className="text-gray-600" />
                          </div>
                        </div>
                      </Card>
                    </Link>
                  </Col>
                ))}
              </Row>

              {/* Pagination */}
              <div className="flex justify-center mt-12">
                <Pagination
                  current={currentPage}
                  pageSize={pageSize}
                  total={displayProducts.length}
                  onChange={handlePaginationChange}
                />
              </div>
            </>
          ) : (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📭</div>
              <p className="text-gray-500 text-lg font-semibold">Không tìm thấy sản phẩm nào</p>
              <p className="text-gray-400 mt-2">Hãy thử tìm kiếm với từ khóa khác hoặc chọn danh mục khác</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

