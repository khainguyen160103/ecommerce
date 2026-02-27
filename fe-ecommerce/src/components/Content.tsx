'use client'
import React from 'react'
import { Layout } from 'antd'

const Content = Layout
export default function ContentComponent({ children, colorBgContainer, borderRadiusLG }) {
  return (
      <Content style={{
          margin: '24px 16px',
          padding: 24,
          minHeight: 280,
          background: colorBgContainer,
          borderRadius: borderRadiusLG,
          overflowY: 'auto',
      }}>{children}</Content>
  )
}
