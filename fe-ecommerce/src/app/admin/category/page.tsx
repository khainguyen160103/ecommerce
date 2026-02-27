'use client'
import React, { useState } from 'react'
import { Button, Flex, Modal, Space, Table, Tag, Popconfirm, Form, Input, message } from 'antd';
import { useCategory } from '@/hook/useCategory';
import Spinner from '@/components/Spinner';
import { formatDate } from '@/utils/formatDate';
import type { PopconfirmProps } from 'antd';

const { Column } = Table;

interface DataType {
  id: string;
  name: string;
  description: string;
  create_at: string;
  update_at: string;
}

export default function CategoryPage() {
  const { categoriesData, deleteMutation, updateMutation, createMutation } = useCategory();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const tableData: DataType[] = categoriesData.data?.data || [];

  const handleAddCategory = () => {
    setEditingId(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: DataType) => {
    setEditingId(record.id);
    form.setFieldsValue({
     name: record.name,
      description: record.description,
    }); 
    setIsModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingId) {
        await updateMutation.mutateAsync({
          id: editingId,
          data: values,
        });
      } else {
        await createMutation.mutateAsync(values);
      }
      
      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.log('Validate Failed:', error);
    }
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  return (
    <>
      {categoriesData.isLoading ? (
        <Spinner />
      ) : (
        <>
          <Button 
            className='w-fit'
            type="primary" 
            style={{ marginBottom: 16 }}
            onClick={handleAddCategory}
          >
            Thêm Danh Mục
          </Button>
          
          <Table<DataType> dataSource={tableData} rowKey="id" scroll={{x: 1200, y: 400}}>
            <Column title="Tên Danh Mục" dataIndex="name" key="name" />
            <Column title="Mô Tả" dataIndex="description" key="description" />
            <Column
              title="Thời Gian Tạo"
              key="create_at"
              dataIndex="create_at"
              render={(date: string) => formatDate(date)}
            />
            <Column
              title="Thời Gian Cập Nhật"
              key="update_at"
              dataIndex="update_at"
              render={(date: string) => formatDate(date)}
            />
            <Column
              title="Tùy Chỉnh"
              key="action"
              render={(_: any, record: DataType) => (
                <Space size="middle">
                  <Button 
                    type="primary"
                    onClick={() => handleEdit(record)}
                  >
                    Sửa
                  </Button>
                  <Popconfirm
                    title="Xóa danh mục"
                    description="Bạn có chắc chắn muốn xóa danh mục này?"
                    onConfirm={() => handleDelete(record.id)}
                    okText="Có"
                    cancelText="Không"
                    okButtonProps={{ danger: true }}
                  >
                    <Button danger>Xóa</Button>
                  </Popconfirm>
                </Space>
              )}
            />
          </Table>

          <Modal
            title={editingId ? "Cập Nhật Danh Mục" : "Thêm Danh Mục"}
            open={isModalVisible}
            onOk={handleModalOk}
            onCancel={() => setIsModalVisible(false)}
            okText={editingId ? "Cập Nhật" : "Thêm"}
            cancelText="Hủy"
          >
            <Form
              form={form}
              layout="vertical"
              style={{ marginTop: 20 }}
            >
              <Form.Item
                label="Tên Danh Mục"
                name="name"
                rules={[
                  { required: true, message: 'Vui lòng nhập tên danh mục' },
                ]}
              >
                <Input placeholder="Nhập tên danh mục" />
              </Form.Item>
              <Form.Item
                label="Mô Tả"
                name="description"
                rules={[
                  { required: true, message: 'Vui lòng nhập mô tả' },
                ]}
              >
                <Input.TextArea 
                  placeholder="Nhập mô tả danh mục"
                  rows={4}
                />
              </Form.Item>
            </Form>
          </Modal>
        </>
      )}
    </>
  );
}
