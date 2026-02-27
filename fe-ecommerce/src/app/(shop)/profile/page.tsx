'use client'
import { useState, useEffect } from 'react'
import { Form, Input, Button, Card, Row, Col, Avatar, Space, Spin, message, Modal } from 'antd'
import { EditOutlined, SaveOutlined, CloseOutlined, LogoutOutlined, ShoppingOutlined, LockOutlined } from '@ant-design/icons'
import { useUsers } from '@/hook/useUser'
import { Authorization, TokenService } from '@/utils/auth.utils'
import { AuthService } from '@/requests/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface UserProfile {
  id: string
  username: string
  email: string
  role: string
  create_at: string
  update_at: string
  status: boolean
}

export default function ProfilePage() {
  const router = useRouter()
  const [form] = Form.useForm()
  const [isEditing, setIsEditing] = useState(false)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [isMounted, setIsMounted] = useState(false)
  const { updateMutation } = useUsers(undefined, { enableGetAll: false })

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (!isMounted) return

    const token = Authorization.getToken()
    const isExpired = TokenService.isTokenExpired()

    if (!token || isExpired) {
      router.push('/login')
      return
    }

    // Lấy thông tin user từ localStorage
    const userInfor = Authorization.getUserInfor()
    if (userInfor) {
      setUserProfile(userInfor)
      form.setFieldsValue({
        username: userInfor.username,
        email: userInfor.email,
        role: userInfor.role,
      })
    }

    setLoading(false)
  }, [isMounted, form, router])

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleCancel = () => {
    setIsEditing(false)
    if (userProfile) {
      form.setFieldsValue({
        username: userProfile.username,
        email: userProfile.email,
        role: userProfile.role,
      })
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()

      if (!userProfile) return

      await updateMutation.mutateAsync({
        id: userProfile.id,
        data: {
          username: values.username,
          email: values.email,
        },
      })

      // Cập nhật state và localStorage
      const updatedProfile = {
        ...userProfile,
        username: values.username,
        email: values.email,
      }
      setUserProfile(updatedProfile)
      Authorization.saveUserInfor(updatedProfile)

      setIsEditing(false)
      message.success('Cập nhật hồ sơ thành công!')
    } catch (error: any) {
      console.error('Validation failed:', error)
      message.error('Cập nhật hồ sơ thất bại!')
    }
  }

  const handleLogout = () => {
    Modal.confirm({
      title: 'Xác nhận đăng xuất',
      content: 'Bạn có chắc chắn muốn đăng xuất?',
      okText: 'Đăng xuất',
      cancelText: 'Hủy',
      okButtonProps: { danger: true },
      onOk: async () => {
        await Authorization.logout()
      },
    })
  }

  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [passwordForm] = Form.useForm()
  const [changingPwLoading, setChangingPwLoading] = useState(false)

  const handleChangePassword = async () => {
    try {
      const values = await passwordForm.validateFields()
      setChangingPwLoading(true)
      await AuthService.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      })
      message.success('Đổi mật khẩu thành công!')
      passwordForm.resetFields()
      setIsChangingPassword(false)
    } catch (error: any) {
      const detail = error?.response?.data?.detail
      message.error(detail || 'Đổi mật khẩu thất bại!')
    } finally {
      setChangingPwLoading(false)
    }
  }

  if (!isMounted || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spin size="large" />
      </div>
    )
  }

  if (!userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Không thể tải thông tin hồ sơ</p>
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Hồ sơ cá nhân</h1>
            <p className="text-gray-600">Quản lý thông tin cá nhân của bạn</p>
          </div>

          {/* Profile Card */}
          <Card className="mb-6 shadow-sm">
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={6} className="flex flex-col items-center">
                <Avatar
                  size={120}
                  style={{ backgroundColor: '#87d068' }}
                >
                  {userProfile.username?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
                <p className="mt-4 font-semibold text-center">{userProfile.username}</p>
              </Col>

              <Col xs={24} sm={18}>
                <Form
                  form={form}
                  layout="vertical"
                  className="space-y-4"
                >
                  <Form.Item
                    label="Tên người dùng"
                    name="username"
                    rules={[
                      { required: true, message: 'Vui lòng nhập tên người dùng' },
                      { min: 3, message: 'Tên người dùng phải có ít nhất 3 ký tự' },
                    ]}
                  >
                    <Input
                      disabled={!isEditing}
                      placeholder="Nhập tên người dùng"
                    />
                  </Form.Item>

                  <Form.Item
                    label="Email"
                    name="email"
                    rules={[
                      { required: true, message: 'Vui lòng nhập email' },
                      { type: 'email', message: 'Email không hợp lệ' },
                    ]}
                  >
                    <Input
                      disabled={!isEditing}
                      type="email"
                      placeholder="Nhập email"
                    />
                  </Form.Item>

                  <Form.Item
                    label="Vai trò"
                    name="role"
                  >
                    <Input
                      disabled={true}
                      placeholder="Vai trò"
                    />
                  </Form.Item>

                  <div className="flex gap-2 flex-wrap">
                    {!isEditing ? (
                      <>
                        <Button
                          type="primary"
                          icon={<EditOutlined />}
                          onClick={handleEdit}
                        >
                          Chỉnh sửa
                        </Button>
                        <Link href="/profile/orders">
                          <Button
                            icon={<ShoppingOutlined />}
                          >
                            Đơn hàng
                          </Button>
                        </Link>
                        <Button
                          danger
                          icon={<LogoutOutlined />}
                          onClick={handleLogout}
                        >
                          Đăng xuất
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          type="primary"
                          icon={<SaveOutlined />}
                          onClick={handleSave}
                          loading={updateMutation.isPending}
                        >
                          Lưu
                        </Button>
                        <Button
                          icon={<CloseOutlined />}
                          onClick={handleCancel}
                        >
                          Hủy
                        </Button>
                      </>
                    )}
                  </div>
                </Form>
              </Col>
            </Row>
          </Card>

          {/* Account Info */}
          <Card title="Thông tin tài khoản" className="shadow-sm">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Trạng thái</p>
                  <p className="font-semibold">
                    {userProfile.status ? (
                      <span className="text-green-600">Hoạt động</span>
                    ) : (
                      <span className="text-red-600">Bị khóa</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Ngày tạo</p>
                  <p className="font-semibold">{formatDate(userProfile.create_at)}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Lần cập nhật cuối</p>
                  <p className="font-semibold">{formatDate(userProfile.update_at)}</p>
                </div>
              </div>
            </Space>
          </Card>

          {/* Change Password */}
          <Card 
            title="Đổi mật khẩu" 
            className="shadow-sm mt-6"
            extra={
              !isChangingPassword ? (
                <Button 
                  icon={<LockOutlined />} 
                  onClick={() => setIsChangingPassword(true)}
                >
                  Đổi mật khẩu
                </Button>
              ) : null
            }
          >
            {isChangingPassword ? (
              <Form
                form={passwordForm}
                layout="vertical"
                style={{ maxWidth: 400 }}
              >
                <Form.Item
                  label="Mật khẩu hiện tại"
                  name="old_password"
                  rules={[{ required: true, message: 'Vui lòng nhập mật khẩu hiện tại' }]}
                >
                  <Input.Password placeholder="Nhập mật khẩu hiện tại" />
                </Form.Item>

                <Form.Item
                  label="Mật khẩu mới"
                  name="new_password"
                  rules={[
                    { required: true, message: 'Vui lòng nhập mật khẩu mới' },
                    { min: 6, message: 'Mật khẩu phải có ít nhất 6 ký tự' },
                  ]}
                >
                  <Input.Password placeholder="Nhập mật khẩu mới" />
                </Form.Item>

                <Form.Item
                  label="Xác nhận mật khẩu mới"
                  name="confirm_password"
                  dependencies={['new_password']}
                  rules={[
                    { required: true, message: 'Vui lòng xác nhận mật khẩu mới' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('new_password') === value) {
                          return Promise.resolve()
                        }
                        return Promise.reject(new Error('Mật khẩu xác nhận không khớp!'))
                      },
                    }),
                  ]}
                >
                  <Input.Password placeholder="Nhập lại mật khẩu mới" />
                </Form.Item>

                <div className="flex gap-2">
                  <Button
                    type="primary"
                    onClick={handleChangePassword}
                    loading={changingPwLoading}
                  >
                    Xác nhận
                  </Button>
                  <Button
                    onClick={() => {
                      setIsChangingPassword(false)
                      passwordForm.resetFields()
                    }}
                  >
                    Hủy
                  </Button>
                </div>
              </Form>
            ) : (
              <p className="text-gray-500">Nhấn nút &quot;Đổi mật khẩu&quot; để thay đổi mật khẩu của bạn.</p>
            )}
          </Card>
        </div>
      </div>
    </>
  )
}

