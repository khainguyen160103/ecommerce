'use client'
import React, { useState } from 'react'
import { Button, Flex, Modal, Space, Table, Tag, Popconfirm, Form, Input, InputNumber, Select, Upload, Pagination } from 'antd';
import { UploadOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useProduct } from '@/hook/useProduct';
import { useCategory } from '@/hook/useCategory';
import Spinner from '@/components/Spinner';
import { formatDate } from '@/utils/formatDate';
import type { UploadFile } from 'antd';
import { DataType, CategoryOption } from '@/types/product';
import { ProductDetail } from '@/models/productDetail';
const { Column } = Table;
const { TextArea } = Input;

export default function ProductPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isDetailListModalVisible, setIsDetailListModalVisible] = useState(false);
  const [isAddDetailModalVisible, setIsAddDetailModalVisible] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<string | undefined>(undefined);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [form] = Form.useForm();
  const [detailForm] = Form.useForm();

  const { productsData, deleteMutation, updateMutation, createMutation, addDetailMutation, deleteDetailMutation, productDetailsData } = useProduct(selectedProductId);
  const { categoriesData } = useCategory();
  
  // Lấy dữ liệu từ API
  const products: DataType[] = productsData.data?.data || [];
  const pagination = productsData.data?.pagination || {pageSize : 10, total_item: 0, totalPages: 0}
  const {pageSize, total_item, totalPages} = pagination
  const totalProducts = productsData.data?.length || 0;
  
  // Lấy chi tiết sản phẩm
  const productDetails = productDetailsData.data?.data || [];

  const categoryOptions: CategoryOption[] = categoriesData.data?.data?.map((cat: any) => ({
    label: cat.name,
    value: cat.id
  })) || [];

  const handleAddProduct = () => {
    setEditingId(null);
    form.resetFields();
    setFileList([]);
    setIsModalVisible(true);
  };

  const handleEdit = (record: DataType) => {
    setEditingId(record.id);
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      price: parseFloat(record.price),
      category_id: record.category_id,
    });
    setFileList([]);
    setIsModalVisible(true);
  };

  const handleViewDetails = (productId: string) => {
    setSelectedProductId(productId);
    setIsDetailListModalVisible(true);
  };

  const handleAddDetail = () => {
    detailForm.resetFields();
    setIsAddDetailModalVisible(true);
  };

  const handleAddDetailOk = async () => {
    try {
      const values = await detailForm.validateFields();
      
      if (selectedProductId) {
        await addDetailMutation.mutateAsync({
          productId: selectedProductId,
          data: values
        });
        setIsAddDetailModalVisible(false);
        detailForm.resetFields();
      }
    } catch (error) {
      console.log('Validate Failed:', error);
    }
  };

  const handleDeleteDetail = ({ productId, detailId }: { productId: string; detailId: string }) => {
    console.log(productId, detailId)
    deleteDetailMutation.mutate({productId,detailId});
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
        const formData = new FormData();
        formData.append('name', values.name);
        formData.append('description', values.description);
        formData.append('price', values.price.toString());
        formData.append('category_id', values.category_id);
        
        fileList.forEach((file) => {
          if (file.originFileObj) {
            formData.append('files', file.originFileObj);
          }
        });

        const res = await createMutation.mutateAsync(formData);
        console.log(res)
      }
      
      setIsModalVisible(false);
      form.resetFields();
      setFileList([]);
    } catch (error) {
      console.log('Validate Failed:', error);
    }
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const handleUploadChange = ({ fileList }: { fileList: UploadFile[] }) => {
    setFileList(fileList);
  };

  const handlePaginationChange = (page: number, size: number) => {
    setCurrentPage(page);
  };

  return (
    <>
      {productsData.isLoading ? (
        <Spinner />
      ) : (
        <>
          <Button 
            className='w-fit'
            type="primary" 
            style={{ marginBottom: 16 }}
            onClick={handleAddProduct}
          >
            Thêm Sản Phẩm
          </Button>
          
          <Table<DataType> 
            dataSource={products} 
            rowKey="id" 
            scroll={{ x: 50 , y: 400}} 
            pagination={{
              current: currentPage,
              pageSize: pageSize,
              total: totalProducts,
              onChange: handlePaginationChange,
              showSizeChanger: false,
              showTotal: (total) => `Tổng ${total} sản phẩm`,
            }}
          >
            <Column title="Tên Sản Phẩm" dataIndex="name" key="name" />
            <Column title="Mô Tả" dataIndex="description" key="description" width={200} />
            <Column 
              title="Giá" 
              dataIndex="price" 
              key="price"
              render={(price: string) => `${parseFloat(price).toLocaleString('vi-VN')} ₫`}
            />
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
              fixed="right"
              width={250}
              render={(_: any, record: DataType) => (
                <Space size="small" wrap>
                  <Button 
                    type="primary"
                    size="small"
                    onClick={() => handleEdit(record)}
                  >
                    Sửa
                  </Button>
                  <Button
                    type="dashed"
                    size="small"
                    onClick={() => handleViewDetails(record.id)}
                  >
                    Chi Tiết
                  </Button>
                  <Popconfirm
                    title="Xóa sản phẩm"
                    description="Bạn có chắc chắn muốn xóa sản phẩm này?"
                    onConfirm={() => handleDelete(record.id)}
                    okText="Có"
                    cancelText="Không"
                    okButtonProps={{ danger: true }}
                  >
                    <Button danger size="small">Xóa</Button>
                  </Popconfirm>
                </Space>
              )}
            />
          </Table>

          {/* Modal Thêm/Sửa Sản Phẩm */}
          <Modal
            title={editingId ? "Cập Nhật Sản Phẩm" : "Thêm Sản Phẩm"}
            open={isModalVisible}
            onOk={handleModalOk}
            onCancel={() => setIsModalVisible(false)}
            okText={editingId ? "Cập Nhật" : "Thêm"}
            cancelText="Hủy"
            width={700}
          >
            <Form
              form={form}
              layout="vertical"
              style={{ marginTop: 20 }}
            >
              <Form.Item
                label="Tên Sản Phẩm"
                name="name"
                rules={[
                  { required: true, message: 'Vui lòng nhập tên sản phẩm' },
                ]}
              >
                <Input placeholder="Nhập tên sản phẩm" />
              </Form.Item>

              <Form.Item
                label="Mô Tả"
                name="description"
                rules={[
                  { required: true, message: 'Vui lòng nhập mô tả' },
                ]}
              >
                <TextArea 
                  placeholder="Nhập mô tả sản phẩm"
                  rows={4}
                />
              </Form.Item>

              <Form.Item
                label="Giá"
                name="price"
                rules={[
                  { required: true, message: 'Vui lòng nhập giá' },
                ]}
              >
                <InputNumber 
                  placeholder="Nhập giá sản phẩm"
                  min={0}
                  step={1000}
                  formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                />
              </Form.Item>

              <Form.Item
                label="Danh Mục"
                name="category_id"
                rules={[
                  { required: true, message: 'Vui lòng chọn danh mục' },
                ]}
              >
                <Select
                  placeholder="Chọn danh mục"
                  options={categoryOptions}
                />
              </Form.Item>

              {!editingId && (
                <Form.Item
                  label="Hình Ảnh"
                  required
                >
                  <Upload
                    fileList={fileList}
                    onChange={handleUploadChange}
                    multiple
                    accept="image/*"
                    beforeUpload={() => false}
                  >
                    <Button icon={<UploadOutlined />}>
                      Chọn Hình Ảnh
                    </Button>
                  </Upload>
                </Form.Item>
              )}
            </Form>
          </Modal>

          {/* Modal Hiển Thị Chi Tiết Sản Phẩm */}
          <Modal
            title="Chi Tiết Sản Phẩm"
            open={isDetailListModalVisible}
            onCancel={() => setIsDetailListModalVisible(false)}
            footer={[
              <Button 
                key="add" 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={handleAddDetail}
              >
                Thêm Chi Tiết
              </Button>,
              <Button 
                key="close" 
                onClick={() => setIsDetailListModalVisible(false)}
              >
                Đóng
              </Button>
            ]}
            width={900}
          >
            <Table
              dataSource={productDetails}
              rowKey="id"
              size="small"
              scroll={{ x: 800 }}
            >
              <Column title="Màu" dataIndex="color" key="color" />
              <Column title="Kích Cỡ" dataIndex="size" key="size" />
              <Column title="Số Lượng" dataIndex="stock" key="stock" />
              <Column title="Cân Nặng (kg)" dataIndex="weight" key="weight" />
              <Column title="Dài (cm)" dataIndex="length" key="length" />
              <Column title="Rộng (cm)" dataIndex="width" key="width" />
              <Column title="Cao (cm)" dataIndex="height" key="height" />
              <Column
                title="Hành Động"
                key="action"
                fixed="right"
                width={100}
                render={(_: any, record: ProductDetail) => (
                  <Popconfirm
                    title="Xóa chi tiết"
                    description="Bạn có chắc chắn muốn xóa?"
                    onConfirm={() => handleDeleteDetail({ 
                      productId: record.product_id, 
                      detailId: record.id
                    })}
                    okText="Có"
                    cancelText="Không"
                    okButtonProps={{ danger: true }}
                  >
                    <Button 
                      danger 
                      size="small" 
                      icon={<DeleteOutlined />}
                    >
                      Xóa
                    </Button>
                  </Popconfirm>
                )}
              />
            </Table>
          </Modal>

          {/* Modal Thêm Chi Tiết Sản Phẩm */}
          <Modal
            title="Thêm Chi Tiết Sản Phẩm"
            open={isAddDetailModalVisible}
            onOk={handleAddDetailOk}
            onCancel={() => setIsAddDetailModalVisible(false)}
            okText="Thêm"
            cancelText="Hủy"
            width={600}
          >
            <Form
              form={detailForm}
              layout="vertical"
              style={{ marginTop: 20 }}
            >
              <Form.Item
                label="Màu"
                name="color"
              >
                <Input placeholder="Nhập màu sản phẩm (optional)" />
              </Form.Item>

              <Form.Item
                label="Kích Cỡ"
                name="size"
              >
                <Input placeholder="Nhập kích cỡ (optional)" />
              </Form.Item>

              <Form.Item
                label="Số Lượng Tồn Kho"
                name="stock"
                rules={[
                  { required: true, message: 'Vui lòng nhập số lượng tồn kho' },
                ]}
              >
                <InputNumber 
                  placeholder="Nhập số lượng"
                  min={0}
                />
              </Form.Item>

              <Form.Item
                label="Cân Nặng (kg)"
                name="weight"
              >
                <InputNumber 
                  placeholder="Nhập cân nặng (optional)"
                  min={0}
                  step={0.1}
                />
              </Form.Item>

              <Form.Item
                label="Chiều Dài (cm)"
                name="length"
              >
                <InputNumber 
                  placeholder="Nhập chiều dài (optional)"
                  min={0}
                />
              </Form.Item>

              <Form.Item
                label="Chiều Rộng (cm)"
                name="width"
              >
                <InputNumber 
                  placeholder="Nhập chiều rộng (optional)"
                  min={0}
                />
              </Form.Item>

              <Form.Item
                label="Chiều Cao (cm)"
                name="height"
              >
                <InputNumber 
                  placeholder="Nhập chiều cao (optional)"
                  min={0}
                />
              </Form.Item>
            </Form>
          </Modal>
        </>
      )}
    </>
  );
}