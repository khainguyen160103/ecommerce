import { Suspense } from "react"
import HeaderTop from "@/components/Header"
import { ChatWidget } from "@/components/ChatWidget"

const HomeLayout = ({children}) => { 
    return <>
    <Suspense>
      <HeaderTop  />
    </Suspense>
    <Suspense>
      {children}
    </Suspense>
    <ChatWidget />
    </>
}


export default HomeLayout