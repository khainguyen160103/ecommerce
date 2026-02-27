'use client'
import React, { useState } from 'react'
import { Button, Flex, Modal, Space, Table, Tag, Popconfirm, Form, Input, Select } from 'antd';
import { useUsers } from '@/hook/useUser';
import Spinner from '@/components/Spinner';
import { formatDate } from '@/utils/formatDate';
import type { PopconfirmProps } from 'antd';
import toast from 'react-hot-toast';
const { Column, ColumnGroup } = Table;

interface DataType {
  id: string;  // <- thêm id
  username: string;
  password? :string
  email: string;
  role: string;
  status: boolean;
  create_at: string;
  update_at: string;
}



export default function UsersPage() {
  const { usersData } = useUsers();
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form] = Form.useForm()
  const tableData: DataType[] = usersData.data?.data || [];

  const confirm: PopconfirmProps['onConfirm'] = (e) => {
    console.log(e);
    toast.success("Xóa Thành Công")
  };

  const cancel: PopconfirmProps['onCancel'] = (e) => {
    console.log(e);
    toast.success("cancel")
  };
  const getPassword = (id: string) => { 
    return tableData.filter(user => user.id === id)['password']
  }
  const handleModalOpen = (record: DataType) => {
      setIsModalVisible(true); 
      console.log(record.id)

      const user = tableData.filter(user => user.id === record.id)
      console.log(user)
      form.setFieldsValue({
        username: record.username,
        email: record.email,
        password: getPassword(record.id),
        role: record.role, 
        status: record.status ? "kích hoạt" : "Vô hiệu hóa" , 
        create_at: formatDate( record.create_at), 
        update_at : formatDate(record.update_at)
      });

  }


  const handleOnOk = () => { 
      setIsModalVisible(false)
  }

  const handleOnCancel = () => { 
    setIsModalVisible(false)

  }
  const handleSelectChange = (value) => { 
    console.log(value)
  }
  return (
    <>
      {usersData.isSuccess ?
        <Table<DataType> dataSource={tableData} rowKey="id">
          <Column title="Tên đăng nhập" dataIndex="username" key="username" />
          <Column title="Email" dataIndex="email" key="email" />
          <Column title="Quyền" dataIndex="role" key="role" />
          <Column
            title="Activate"
            dataIndex="status"
            key="status"
            render={(isActivate: boolean) => (
              <Flex gap="small" align="center" wrap>
                <Tag color={isActivate ? 'blue' : 'red'}>
                  {isActivate ? "Kích hoạt" : "Vô Hiệu Hóa"}
                </Tag>
              </Flex>
            )}
          />
          <Column
            title="Thời Gian Kích Hoạt"
            key="create_at"
            dataIndex='create_at'
            render={(date: string) => formatDate(date)}
          />
          <Column
            title="Thời Gian Cập Nhật"
            key="update_at"
            dataIndex='update_at'
            render={(date: string) => formatDate(date)}
          />
          <Column
            title="Tùy Chỉnh"
            key="action"
            render={(_: any, record: DataType) => (
              <Space size="middle">
                <Button onClick={() => handleModalOpen(record)}>Xem chi tiết</Button>
                <Popconfirm
                  title="Xóa người dùng"
                  description="bạn có chắc chắn muốn xóa người dùng này"
                  onConfirm={confirm}
                  onCancel={cancel}
                  okText="Yes"
                  cancelText="No"
                  okButtonProps={{ danger: true }}
                >
                  <Button danger>Xóa</Button>
                </Popconfirm>
              </Space>
            )}
          />
        </Table>
        : <Spinner />}
      <Modal
      
      open={isModalVisible}
      onOk={handleOnOk}
      onCancel={handleOnCancel}>
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            
            label="Tên đăng nhập"
            name='username'
          >
            <Input readOnly placeholder='Username' />
          </Form.Item>
          <Form.Item
            label="Email"
            name='email'
          >
            <Input readOnly placeholder='Email' />
          </Form.Item>
          <Form.Item
            label="Quyền"
            name='role'
          >
            <Select
              defaultValue="lucy"
              style={{ width: 120 }}
              onChange={handleSelectChange}
              options={[
                { value: 'ADMIN', label: 'ADMIN' },
                { value: 'USER', label: 'USER' },
              ]}
            />
          </Form.Item>
          <Form.Item
            label="Activate"
            name='status'
          >
            <Input placeholder='Trạng thái' />
          </Form.Item>
          <Form.Item
            label="Thời gian kích hoạt"
            name='create_at'
          >
            <Input readOnly placeholder='Thời gian kích hoạt' />
          </Form.Item>
          <Form.Item
            label="Thời gian cập nhật"
            name='update_at'
          >
            <Input readOnly  placeholder='Thời gian cập nhật' />
          </Form.Item>
        </Form>

      </Modal>
    </>

  )
}
