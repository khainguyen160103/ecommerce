'use client'
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { TokenService } from "./auth.utils"
import { Authorization } from "./auth.utils"
import Spinner from "@/components/Spinner"
const ProtectRoute = ({ children, roleRequired = 'ADMIN' }) => {
    const router = useRouter()
    // const user = useAppSelector(state => state.auth.user)
    const user = Authorization.getUserInfor()
    const isToken = TokenService.isTokenExpired()
    useEffect(() => {
        if (isToken) {
            router.push('/login')
        } else if (user.role !== roleRequired) {
            router.replace('/home')
        }
    }, [user, router,isToken, roleRequired])
    if (!user || user.role!== roleRequired || isToken) return <Spinner />
    return children
}

export default ProtectRoute