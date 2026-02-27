"use client";

import React, { useRef, useEffect, useState } from "react";
import { MessageOutlined, CloseOutlined, DeleteOutlined } from "@ant-design/icons";
import { useChat } from "@/hook/useChat";
import ChatBubble from "./ChatBubble";
import ChatInput from "./ChatInput";

const QUICK_ACTIONS = [
  "Tìm trang sức handmade",
  "Có sản phẩm nào đang giảm giá không?",
  "Hướng dẫn đặt hàng",
  "Chính sách đổi trả hàng",
];

const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, isConnected, isLoading, sendMessage, clearMessages } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll khi có tin nhắn mới
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleQuickAction = (action: string) => {
    sendMessage(action);
  };

  // Chỉ hiện quick actions khi chỉ có welcome message
  const showQuickActions = messages.length <= 1;

  return (
    <>
      {/* Chat Popup */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-6 z-50 flex flex-col bg-white rounded-2xl overflow-hidden"
          style={{
            width: 370,
            height: 520,
            boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
          }}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between px-4 py-3"
            style={{ backgroundColor: "#52c41a" }}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold text-lg">H</span>
              </div>
              <div>
                <div className="text-white font-semibold text-sm">
                  Trợ lý Handmade
                </div>
                <div className="flex items-center gap-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      isConnected ? "bg-green-200" : "bg-red-300"
                    }`}
                  />
                  <span className="text-green-100 text-xs">
                    {isConnected ? "đang hoạt động" : "đang kết nối..."}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearMessages}
                className="text-white/80 hover:text-white transition-colors p-1"
                title="Xóa hội thoại"
              >
                <DeleteOutlined style={{ fontSize: 16 }} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors p-1"
              >
                <CloseOutlined style={{ fontSize: 18 }} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto px-4 py-3"
            style={{ backgroundColor: "#fafafa" }}
          >
            {messages.map((msg) => (
              <ChatBubble key={msg.id} message={msg} />
            ))}

            {/* Quick Actions */}
            {showQuickActions && (
              <div className="flex flex-col gap-2 mt-2">
                {QUICK_ACTIONS.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action)}
                    className="text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-xl hover:bg-green-50 hover:border-green-300 transition-all text-gray-700"
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center text-white shadow-lg hover:scale-105 active:scale-95 transition-all"
        style={{ backgroundColor: "#52c41a" }}
      >
        {isOpen ? (
          <CloseOutlined style={{ fontSize: 22 }} />
        ) : (
          <MessageOutlined style={{ fontSize: 24 }} />
        )}
      </button>
    </>
  );
};

export default ChatWidget;
