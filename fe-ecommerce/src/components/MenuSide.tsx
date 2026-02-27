'use client'
import { Layout , Menu } from 'antd'
import Link from 'next/link';
import { LayoutDashboard } from 'lucide-react';
import { menuItems } from '@/data/menu';
const {Sider} = Layout
export default function MenuSide({collapsed}) {
    const items = menuItems.map(item =>( { 
        key: item.key, 
        label : <Link href={item.href}>{item.label}</Link>,
        icon: item.icon
    }))
  return (
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className='w-full flex items-center justify-center p-10' > 
        <LayoutDashboard color='white'/> 
        </div>
          <Menu
              theme="dark"
              mode="inline"
              defaultSelectedKeys={['orders']}
              items={items}
          />
      </Sider>
  )
}
