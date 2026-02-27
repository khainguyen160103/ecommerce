"use client";
import HeaderTop from "@/components/Header";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Divider, Input, Tooltip } from "antd";
import { useForm, Controller, SubmitHandler } from "react-hook-form";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import Spinner from "@/components/Spinner";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";
import { GoogleLogin } from "@react-oauth/google";
import { useCallback } from "react";

interface FormInput {
    email: string;
    password: string;
}
export default function Login() {
    const router = useRouter()
    const { login, loading, error, googleLogin } = useAuth()
    const { control, handleSubmit, formState: { isSubmitted } } = useForm({
        defaultValues: { email: "", password: "" },
    });

    const handleOAuthSuccess = useCallback(async (userInfor: any) => {
        if (userInfor?.status === 200) {
            if (userInfor.data.role === "ADMIN") {
                router.push('/admin/order')
            } else {
                router.push('/')
            }
        }
    }, [router])

    const onSubmit: SubmitHandler<FormInput> = async (data: FormInput) => {
        console.log("Received values of form: ", data);
        try { 
            const res = await login(data.email, data.password)
            if(res?.status === 200) { 
                if(res.data.role === "ADMIN") { 
                    router.push('/admin/order')
                }else { 
                    router.push('/')
                }
            }
            if(loading) return <Spinner />
            if(error) return toast.error(error)
        }catch(error) { 
            console.log(error)
        }
        
    };

    const handleGoogleSuccess = async (credentialResponse: any) => {
        if (credentialResponse.credential) {
            const res = await googleLogin(credentialResponse.credential)
            await handleOAuthSuccess(res)
        }
    }

    return (
        <>
            <HeaderTop />
            <div className="flex items-center justify-center flex-col mt-[60px]">
                <div className="bg-white shadow-lg flex items-center flex-col p-9 rounded-2xl min-w-[400px]">
                    <h1 className="text-center mb-10 font-bold">
                        Đăng nhập vào hệ thống để mua hàng
                    </h1>
                    <form className="w-full" onSubmit={handleSubmit(onSubmit)}>
                        <div className="flex flex-col gap-y-2">
                            <div>Email</div>
                            <Controller
                                name="email"
                                rules={{
                                    required: "Vui lòng nhập đầy đủ thông tin",
                                    pattern: {
                                        value: /\S+@\S+\.\S+/,
                                        message: "Email không hợp lệ",
                                    },
                                }}
                                control={control}
                                render={({ field, fieldState }) => (
                                    <Tooltip color={"#ED212C"} placement="topRight" title={fieldState.error?.message ?? " "} open={!!fieldState.error && isSubmitted}>
                                        <Input
                                            {...field}
                                            size="large"
                                            prefix={<UserOutlined />}
                                            placeholder="Email"
                                        />
                                    </Tooltip>
                                )}
                            />
                        </div>
                        <div className="flex flex-col gap-y-2 my-5">
                            <div>Password</div>
                            <Controller
                                name="password"
                                control={control}
                                rules={{ required: "Vui lòng nhập mật khẩu" }}
                                render={({ field, fieldState }) => (
                                    <Tooltip color={"#ED212C"} placement="topRight" title={fieldState.error?.message ?? " "} open={!!fieldState.error && isSubmitted}>
                                        <Input
                                            {...field}
                                            prefix={<LockOutlined />}
                                            type="password"
                                            placeholder="Password"
                                        />
                                    </Tooltip>
                                )}
                            />
                        </div>
                        <Button className="my-2 py-1.5" block type="primary" htmlType="submit" loading={loading}>
                            Đăng nhập
                        </Button>
                        or <Link className="mt-1" href="/register">Đăng ký</Link>
                    </form>
                    
                    <Divider plain>Hoặc đăng nhập bằng</Divider>
                    
                    <div className="flex flex-col items-center gap-3 w-full">
                        <div className="w-full flex justify-center">
                            <GoogleLogin
                                onSuccess={handleGoogleSuccess}
                                onError={() => toast.error("Đăng nhập Google thất bại")}
                                width="100%"
                                text="signin_with"
                                shape="rectangular"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
