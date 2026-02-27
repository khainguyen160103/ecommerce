'use client'

import React from "react";
import { Provider } from "react-redux";
import { store } from "./index";
import type { ReactNode } from "react";

const StoreProvider = ({children} : {children : ReactNode}) => { 
    return <Provider store={store}> 
        {children}
    </Provider>
}

export default StoreProvider