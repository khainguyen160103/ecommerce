import { Dropdown, Space } from 'antd'
import React from 'react'
import type { MenuProps } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import { Bell } from 'lucide-react';

const items: MenuProps['items'] = [
    {
        label: (
            <a href="https://www.antgroup.com" target="_blank" rel="noopener noreferrer">
                bạn vừa có 1 đơn hàng mới vui lòng kiểm tra
            </a>
        ),
        key: '0',
    },
    {
        label: (
            <a href="https://www.aliyun.com" target="_blank" rel="noopener noreferrer">
                2nd menu item
            </a>
        ),
        key: '1',
    },
    {
        type: 'divider',
    },
    {
        label: '3rd menu item',
        key: '3',
    },
];

export default function Notification() {
  return (
      <Dropdown className='mt-2' menu={{ items }} trigger={['click']}>
          <a onClick={(e) => e.preventDefault()}>
                  <Bell className='mr-8' />
          </a>
      </Dropdown>
  )
}
