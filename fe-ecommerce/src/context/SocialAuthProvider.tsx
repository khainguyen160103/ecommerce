'use client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { createContext, ReactNode, useContext, useCallback, useEffect, useRef, useState } from 'react'

const GOOGLE_CLIENT_ID = "880444394894-ub0eejgtqhvs0qcpbds0k4u5v44oga5f.apps.googleusercontent.com"
const FACEBOOK_APP_ID = "2307573336419669"

declare global {
    interface Window {
        FB: any
        fbAsyncInit: () => void
    }
}

interface FacebookSDKContextType {
    isFBReady: boolean
}

const FacebookSDKContext = createContext<FacebookSDKContextType>({ isFBReady: false })

export function useFacebookSDK() {
    return useContext(FacebookSDKContext)
}

function FacebookSDKProvider({ children }: { children: ReactNode }) {
    const [isFBReady, setIsFBReady] = useState(() => {
        // Check if FB SDK is already loaded (e.g., cached/previous navigation)
        if (typeof window !== 'undefined' && window.FB) {
            return true
        }
        return false
    })
    const initCalledRef = useRef(false)

    const initFB = useCallback(() => {
        if (initCalledRef.current) return
        if (window.FB) {
            initCalledRef.current = true
            window.FB.init({
                appId: FACEBOOK_APP_ID,
                cookie: true,
                xfbml: true,
                status: true,
                version: 'v21.0'
            })
            setIsFBReady(true)
            console.log('[FacebookSDK] Initialized successfully')
        }
    }, [])

    useEffect(() => {
        // If FB SDK is already loaded, nothing to do (handled by initial state)
        if (window.FB) {
            // Still need to call FB.init if not done yet
            if (!initCalledRef.current) {
                // Use setTimeout to avoid synchronous setState in effect
                setTimeout(() => initFB(), 0)
            }
            return
        }

        // Set the async init callback for when the SDK loads
        window.fbAsyncInit = function () {
            initFB()
        }

        // Load the SDK script if not already in the DOM
        if (!document.getElementById('facebook-jssdk')) {
            const script = document.createElement('script')
            script.id = 'facebook-jssdk'
            script.src = 'https://connect.facebook.net/vi_VN/sdk.js'
            script.async = true
            script.defer = true
            script.crossOrigin = 'anonymous'
            script.onerror = () => {
                console.error('[FacebookSDK] Failed to load script. Check network or ad blocker.')
            }
            // Fallback: if fbAsyncInit doesn't fire, init on script load
            script.onload = () => {
                if (window.FB && !initCalledRef.current) {
                    initFB()
                }
            }
            document.body.appendChild(script)
        }
    }, [initFB])

    return (
        <FacebookSDKContext.Provider value={{ isFBReady }}>
            {children}
        </FacebookSDKContext.Provider>
    )
}

export default function SocialAuthProvider({ children }: { children: ReactNode }) {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <FacebookSDKProvider>
                {children}
            </FacebookSDKProvider>
        </GoogleOAuthProvider>
    )
}
