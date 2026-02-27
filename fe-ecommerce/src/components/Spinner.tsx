import React from 'react'
import { Spin } from 'antd'
export default function Spinner() {
  return (
    <div className='w-screen h-screen flex justify-center items-center'>
        <Spin size="large" />
    </div>
  )
}
