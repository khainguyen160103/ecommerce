import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import QueryProvider from "@/hook";
import { Layout, Menu, } from "antd";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import StoreProvider from "@/stores/StoreProvider";
import { AuthProvider } from "@/context/AuthContext";
import SocialAuthProvider from "@/context/SocialAuthProvider";
import { Toaster } from "react-hot-toast";
import "./globals.css";
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});
import TopLoader from "@/components/TopLoader";
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ecommerce App",
  description: "Ecommerce App",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AntdRegistry>
          <Layout className="">
            <TopLoader />
            <StoreProvider >
              <SocialAuthProvider>
              <AuthProvider>
                <QueryProvider>
                  <Toaster position={"top-center"} toastOptions={{ style: { 
                    width : "100vw"
                  }}}/>
                  <div className="h-screen w-screen">
                    {children}
                  </div>
                </QueryProvider>
              </AuthProvider>
              </SocialAuthProvider>
            </StoreProvider>
          </Layout>
        </AntdRegistry>
      </body>
    </html>
  );
}
