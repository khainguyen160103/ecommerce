import { Button } from 'antd'
import { Header } from 'antd/es/layout/layout'
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Bell } from 'lucide-react';
import Notification from './Notification';

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
          <Notification />
      </Header>
  )
}
