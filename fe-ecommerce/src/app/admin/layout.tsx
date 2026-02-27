import ProtectRoute from "@/utils/protectRoute"
import type { ReactNode } from "react";
import AdminLayout from "@/components/AdminLayout";
interface DashboardLayout { 
    children: ReactNode 
}
const DashboardLayout = ({ children }: DashboardLayout) => { 
    return <ProtectRoute> 
        <AdminLayout> 
        {children}
        </AdminLayout>
    </ProtectRoute>
}


export default DashboardLayout;