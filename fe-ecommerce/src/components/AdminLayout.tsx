'use client'
import { useState } from 'react'; import type { ReactNode } from "react";
import { Layout, theme } from 'antd'
import MenuSide from '@/components/MenuSide'
import HeaderAdminLayout from '@/components/HeaderAdminLayout';
import ContentComponent from '@/components/Content'
interface AdminLayoutProps { 
    children: ReactNode
}

const AdminLayout = ({children}: AdminLayoutProps) => { 
    const [collapsed, setCollapsed] = useState(false); const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return <Layout style={{ minHeight: '100vh' }}>
        <MenuSide collapsed={collapsed} />
        <Layout style={{ overflow: 'hidden' }}>
            <HeaderAdminLayout colorBgContainer={colorBgContainer} collapsed={collapsed} setCollapsed={setCollapsed} />
            <ContentComponent borderRadiusLG={borderRadiusLG} colorBgContainer={colorBgContainer}>
                {children}
            </ContentComponent>
        </Layout>
    </Layout>
}

export default AdminLayout;