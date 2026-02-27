"use client";

import { useState, useRef, useCallback, useEffect } from "react";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

interface UseChatReturn {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  sendMessage: (message: string) => void;
  clearMessages: () => void;
}

const WS_URL = "ws://127.0.0.1:8000/api/chat/ws";

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Xin chào! hMADE xin vui lòng được hỗ trợ bạn. Bạn cần tư vấn gì hôm nay?",
};

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentBotMessageIdRef = useRef<string | null>(null);
  const connectRef = useRef<() => void>(() => {});

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setIsConnected(true);
        console.log("[Chat] WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === "chunk") {
            const botId = currentBotMessageIdRef.current;
            if (botId) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === botId
                    ? { ...msg, content: msg.content + data.content }
                    : msg
                )
              );
            }
          } else if (data.type === "done") {
            const botId = currentBotMessageIdRef.current;
            if (botId) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === botId ? { ...msg, isStreaming: false } : msg
                )
              );
            }
            currentBotMessageIdRef.current = null;
            setIsLoading(false);
          } else if (data.type === "error") {
            const botId = currentBotMessageIdRef.current;
            if (botId) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === botId
                    ? {
                        ...msg,
                        content: data.content || "Đã xảy ra lỗi, vui lòng thử lại.",
                        isStreaming: false,
                      }
                    : msg
                )
              );
            }
            currentBotMessageIdRef.current = null;
            setIsLoading(false);
          }
        } catch (err) {
          console.error("[Chat] Parse error:", err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("[Chat] WebSocket disconnected");
        // Auto reconnect sau 3s
        reconnectTimeoutRef.current = setTimeout(() => {
          connectRef.current();
        }, 3000);
      };

      ws.onerror = (err) => {
        console.error("[Chat] WebSocket error:", err);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("[Chat] Connection failed:", err);
    }
  }, []);

  // Keep ref in sync
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  const sendMessage = useCallback(
    (message: string) => {
      if (!message.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        // Nếu chưa connect, thử reconnect
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          connect();
        }
        return;
      }

      // Thêm message của user
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
      };

      // Tạo placeholder cho bot response
      const botMsgId = `bot-${Date.now()}`;
      const botMsg: ChatMessage = {
        id: botMsgId,
        role: "assistant",
        content: "",
        isStreaming: true,
      };

      currentBotMessageIdRef.current = botMsgId;
      setMessages((prev) => [...prev, userMsg, botMsg]);
      setIsLoading(true);

      // Build history (giới hạn 10 cặp gần nhất, bỏ welcome message)
      const historyForServer = messages
        .filter((m) => m.id !== "welcome")
        .slice(-20)
        .map((m) => ({
          role: m.role,
          content: m.content,
        }));

      wsRef.current.send(
        JSON.stringify({
          message: message,
          history: historyForServer,
        })
      );
    },
    [messages, connect]
  );

  const clearMessages = useCallback(() => {
    setMessages([WELCOME_MESSAGE]);
    currentBotMessageIdRef.current = null;
    setIsLoading(false);
  }, []);

  return {
    messages,
    isConnected,
    isLoading,
    sendMessage,
    clearMessages,
  };
}
