"use client";

import React, { useState, KeyboardEvent } from "react";
import { SendOutlined } from "@ant-design/icons";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled = false }) => {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center gap-2 p-3 border-t border-gray-200 bg-white">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Nhập tin nhắn..."
        disabled={disabled}
        className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-full outline-none focus:border-green-500 transition-colors disabled:bg-gray-50 disabled:text-gray-400"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="flex items-center justify-center w-9 h-9 rounded-full text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 active:scale-95"
        style={{ backgroundColor: "#52c41a" }}
      >
        <SendOutlined style={{ fontSize: 16 }} />
      </button>
    </div>
  );
};

export default ChatInput;
