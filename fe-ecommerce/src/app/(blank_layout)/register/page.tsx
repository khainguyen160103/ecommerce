'use client'
import React from 'react';
import type { FormItemProps, FormProps } from 'antd';
import {
  Button,
  Divider,
  Form,
  Input,
} from 'antd';
import HeaderTop from '@/components/Header';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { GoogleLogin } from '@react-oauth/google';
import { Facebook } from 'lucide-react';
import Link from 'next/link';
import { useFacebookSDK } from '@/context/SocialAuthProvider';

const formItemLayout: FormProps = {
  labelCol: {
    xs: { span: 24 },
    sm: { span: 8 },
  },
  wrapperCol: {
    xs: { span: 24 },
    sm: { span: 16 },
  },
};

const tailFormItemLayout: FormItemProps = {
  wrapperCol: {
    xs: {
      span: 24,
      offset: 0,
    },
    sm: {
      span: 16,
      offset: 8,
    },
  },
};

const Register: React.FC = () => {
  const [form] = Form.useForm();
  const { register, loading, googleLogin, facebookLogin } = useAuth();
  const { isFBReady } = useFacebookSDK();
  const router = useRouter();

  const onFinish = async (values: any) => {
    try {
      const res = await register(values.email.split('@')[0], values.email, values.password);
      if (res?.status === 200) {
        toast.success('Đăng ký thành công! Vui lòng đăng nhập.');
        router.push('/login');
      }
    } catch (error: any) {
      console.log('Register error:', error);
    }
  };

  const handleOAuthSuccess = async (userInfor: any) => {
    if (userInfor?.status === 200) {
      if (userInfor.data.role === "ADMIN") {
        router.push('/admin/order')
      } else {
        router.push('/')
      }
    }
  }

  const handleGoogleSuccess = async (credentialResponse: any) => {
    if (credentialResponse.credential) {
      const res = await googleLogin(credentialResponse.credential)
      await handleOAuthSuccess(res)
    }
  }

  const handleFacebookLogin = () => {
    if (typeof window === 'undefined') return

    if (!window.FB || !isFBReady) {
      toast.error("Facebook SDK chưa sẵn sàng, vui lòng thử lại sau vài giây")
      console.error('[FacebookLogin] FB SDK not ready. window.FB:', !!window.FB, 'isFBReady:', isFBReady)
      return
    }

    window.FB.login((response: any) => {
      if (response.authResponse) {
        const { accessToken } = response.authResponse
        facebookLogin(accessToken).then(handleOAuthSuccess)
      } else {
        console.warn('[FacebookLogin] Login cancelled or no authResponse:', response)
        toast.error("Đăng nhập Facebook bị hủy")
      }
    }, { scope: 'email,public_profile' })
  }

  return (
    <> 
    <HeaderTop />
    <div className='h-screen flex items-center justify-center flex-col'>  
        <div className='bg-white shadow-lg flex items-center flex-col p-9 rounded-2xl min-w-[450px]'>
      <h1 className='mb-4'><strong>Đăng ký tài khoản</strong></h1> 
    <Form
      {...formItemLayout}
      form={form}
      name="register"
      onFinish={onFinish}
      initialValues={{}}
      style={{ maxWidth: 600 }}
      scrollToFirstError
    >
      <Form.Item
        name="email"
        label="E-mail"
        rules={[
          {
            type: 'email',
            message: 'Email không hợp lệ!',
          },
          {
            required: true,
            message: 'Vui lòng nhập E-mail!',
          },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        name="password"
        label="Mật khẩu"
        rules={[
          {
            required: true,
            message: 'Vui lòng nhập mật khẩu!',
          },
          {
            min: 6,
            message: 'Mật khẩu phải có ít nhất 6 ký tự!',
          },
        ]}
        hasFeedback
      >
        <Input.Password />
      </Form.Item>

      <Form.Item
        name="confirm"
        label="Xác nhận mật khẩu"
        dependencies={['password']}
        hasFeedback
        rules={[
          {
            required: true,
            message: 'Vui lòng xác nhận mật khẩu!',
          },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('Mật khẩu xác nhận không khớp!'));
            },
          }),
        ]}
      >
        <Input.Password />
      </Form.Item>

      <Form.Item {...tailFormItemLayout}>
        <Button block type="primary" htmlType="submit" loading={loading}>
          Đăng Ký
        </Button>
        <div className="mt-2 text-center">
          Đã có tài khoản? <Link href="/login">Đăng nhập</Link>
        </div>
      </Form.Item>
    </Form>

    <Divider plain>Hoặc đăng ký bằng</Divider>

    <div className="flex flex-col items-center gap-3 w-full px-4">
      <div className="w-full flex justify-center">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => toast.error("Đăng nhập Google thất bại")}
          width="100%"
          text="signup_with"
          shape="rectangular"
        />
      </div>
      <Button
        size="large"
        icon={<Facebook size={18} />}
        block
        type="primary"
        onClick={handleFacebookLogin}
        disabled={!isFBReady}
        style={{ backgroundColor: '#1877F2' }}
      >
        {isFBReady ? 'Đăng ký với Facebook' : 'Đang tải Facebook SDK...'}
      </Button>
    </div>

    </div>
    </div>
    </>
  );
};

export default Register;