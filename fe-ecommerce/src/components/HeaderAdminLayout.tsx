import { Button } from 'antd'
import { Header } from 'antd/es/layout/layout'
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
} from '@ant-design/icons';

export default function HeaderAdminLayout({ colorBgContainer,  collapsed , setCollapsed}) {
  return (
      <Header style={{ padding: 0, background: colorBgContainer }} className='flex justify-between items-center'>
          <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                  fontSize: '16px',
                  width: 64,
                  height: 64,
              }}
          />
          <Button className='mr-5' type='dashed' href='/home'>Trang chủ</Button>
      </Header>
  )
}
