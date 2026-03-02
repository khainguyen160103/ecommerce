'use client'
import { useState } from 'react'
import Image from 'next/image';
import Link from 'next/link';
import { Flex, Layout, Input, Dropdown, Avatar, Badge, Button } from 'antd';
import type { MenuProps } from 'antd';
import { ShoppingCart, Menu, X } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { Authorization } from '@/utils/auth.utils';
import { SearchOutlined, CloseCircleFilled } from "@ant-design/icons";
import { useSearch } from '@/hook/useSearch';
import { useAuth } from '@/context/AuthContext';
import { useCart } from '@/hook/useCart';
const { Header } = Layout;
const { Search } = Input

export default function HeaderTop() {
  const pathname = usePathname()
  const {checkAuth} = useAuth()
  const { inputValue, handleSearch, handleSearchImmediate, clearSearch } = useSearch()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const { useGetMyCart } = useCart()
  const { data: cartData } = useGetMyCart()
  const cartCount = cartData?.total_items || 0


  const userInfor = Authorization.getUserInfor()
  // useEffect(() => {
  //   const isExpired = TokenService.isTokenExpired()
    
  //   if (isExpired && !checkAuth() && !userInfor) { 
  //     return router.push('/login')
  //   }
  // }, [checkAuth, router, userInfor])

  const handleLogout = async () => {
    await Authorization.logout()
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: '1',
      label: <Link href="/profile">Thông tin cá nhân</Link>,
    },
    {
      key: '2',
      label: <Link href="/profile/orders">Đơn hàng của tôi</Link>,
    },
    {
      key: '3',
      label: <Link href="/settings">Cài đặt</Link>,
    },
    {
      type: 'divider',
    },
    {
      key: '4',
      label: 'Đăng xuất',
      danger: true,
      onClick: handleLogout,
    },
  ];

  const isAuthPage = pathname === '/login' || pathname === "/register"

  return (
    <>
      <Header className="!px-0 !h-auto sticky top-0 z-50 !shadow-md" style={{ backgroundColor: '#52c41a' }}>
        <div className="max-w-[1440px] h-full mx-auto w-full px-4 sm:px-6 lg:px-8">
          {/* Top Bar - Logo, Search, User Actions */}
          <div className="flex items-center justify-between gap-4 py-3">
            <Link href='/' className="flex-none">
              <div className="w-[45px] h-[45px] rounded-full overflow-hidden">
                <Image alt='logo' width={45} height={45} src="/Planet Knit Logo.jpg" priority className="object-cover w-full h-full" />
              </div>
            </Link>
            
            {!isAuthPage && (
              <>
                {/* Search Bar */}
                <div className="flex-1 hidden md:flex">
                  <Input
                    size="large"
                    placeholder="Tìm kiếm sản phẩm..."
                    prefix={<SearchOutlined className="text-green-600" />}
                    value={inputValue}
                    onChange={(e) => handleSearch(e.target.value)}
                    onPressEnter={(e) => handleSearchImmediate((e.target as HTMLInputElement).value)}
                    suffix={
                      inputValue ? (
                        <CloseCircleFilled
                          className="text-gray-400 hover:text-gray-600 cursor-pointer"
                          onClick={clearSearch}
                        />
                      ) : null
                    }
                    allowClear={false}
                    className="rounded-lg"
                  />
                </div>

                {/* User Section */}
                <div className="flex items-center gap-4 flex-none">
                  {checkAuth() && userInfor ? (
                    <>
                      {/* Desktop - User Avatar */}
                      <div className="hidden sm:block">
                        <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
                          <Flex gap="small" align="center" className="cursor-pointer hover:opacity-80 transition">
                            <Avatar 
                              size="large" 
                              style={{ backgroundColor: '#fff', color: '#52c41a', fontWeight: 'bold' }}
                            >
                              {userInfor?.username?.charAt(0).toUpperCase() || 'U'}
                            </Avatar>
                            <div className="hidden lg:block">
                              <p className="text-sm font-semibold mb-0 text-white">{userInfor?.username}</p>
                              <p className="text-xs text-green-100 mb-0">{userInfor?.email}</p>
                            </div>
                          </Flex>
                        </Dropdown>
                      </div>

                      {/* Cart Icon */}
                      <Link href="/cart">
                        <Badge count={cartCount} overflowCount={99} size="small">
                          <ShoppingCart className="w-6 h-6 text-white hover:text-green-100 transition cursor-pointer" />
                        </Badge>
                      </Link>
                    </>
                  ) : (
                    <>
                      <Link href="/login">
                          <Button type="default" size="large" className="!border-white !text-white hover:!bg-white/10">Đăng nhập</Button>
                      </Link>
                      <Link href="/register">
                          <Button type="primary" size="large" className="!bg-white !text-green-600 !border-white hover:!bg-green-50">Đăng ký</Button>
                      </Link>
                      <Link href="/cart">
                        
                          <ShoppingCart className="w-6 h-6 text-white" />
                        
                      </Link>
                    </>
                  )}

                  {/* Mobile Menu Button */}
                  <button 
                    className="md:hidden text-white"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  >
                    {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Mobile Search Bar */}
          {!isAuthPage && (
            <div className="md:hidden pb-3 border-t pt-3">
              <Search 
                size="large" 
                placeholder="Tìm kiếm sản phẩm..." 
                value={inputValue}
                onChange={(e) => handleSearch(e.target.value)}
                onSearch={(value) => handleSearchImmediate(value)}
                enterButton="Tìm"
                allowClear
                onClear={clearSearch}
                className="!rounded-lg"
              />
            </div>
          )}
        </div>
      </Header>

      {/* Mobile Menu */}
      {!isAuthPage && mobileMenuOpen && checkAuth() && (
        <div className="md:hidden bg-gray-50 border-b py-3 px-4">
          <div className="flex flex-col gap-3">
            <Link href="/profile" className="px-4 py-2 hover:bg-gray-200 rounded">Thông tin cá nhân</Link>
            <Link href="/profile/orders" className="px-4 py-2 hover:bg-gray-200 rounded">Đơn hàng của tôi</Link>
            <Link href="/settings" className="px-4 py-2 hover:bg-gray-200 rounded">Cài đặt</Link>
            <button onClick={handleLogout} className="px-4 py-2 hover:bg-red-100 text-red-600 rounded text-left">Đăng xuất</button>
          </div>
        </div>
      )}
    </>
  )
}
