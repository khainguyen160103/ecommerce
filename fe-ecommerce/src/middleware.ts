import { NextResponse, NextRequest } from "next/server";


const authMidleware = (request : NextRequest) => {
    
}

export function middleware (request: NextRequest) {
  const protectedRoutes = ['/admin','/cart' ]
  const pathname = request.nextUrl.pathname
    
  const isProtectedRoute = protectedRoutes.some((path) => path === pathname)
  console.log("check" , isProtectedRoute);

  return NextResponse.next();
};


export const config = { 
    matcher : ['/home/:path*', "/product/:path*"]
}