"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ProductService } from "@/requests/product";
import _ from "lodash";

export const useSearch = () => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Lấy keyword từ URL query param ?q=...
  const keyword = searchParams.get("q") || "";
  const [inputValue, setInputValue] = useState(keyword);

  // Sync input khi URL thay đổi (vd: back button)
  useEffect(() => {
    setInputValue(keyword);
  }, [keyword]);

  // Debounce: cập nhật URL sau 500ms ngừng gõ
  const debouncedNavigate = useMemo(
    () =>
      _.debounce((value: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value.trim()) {
          params.set("q", value.trim());
        } else {
          params.delete("q");
        }
        const query = params.toString();
        const target = pathname === "/home" || pathname === "/"
          ? `/home${query ? `?${query}` : ""}`
          : `/home${query ? `?${query}` : ""}`;
        router.push(target);
      }, 500),
    [router, pathname, searchParams]
  );

  // Handler cho input onChange
  const handleSearch = useCallback(
    (value: string) => {
      setInputValue(value);
      debouncedNavigate(value);
    },
    [debouncedNavigate]
  );

  // Tìm kiếm ngay (Enter / click button)
  const handleSearchImmediate = useCallback(
    (value: string) => {
      debouncedNavigate.cancel();
      setInputValue(value);
      const params = new URLSearchParams(searchParams.toString());
      if (value.trim()) {
        params.set("q", value.trim());
      } else {
        params.delete("q");
      }
      const query = params.toString();
      router.push(`/home${query ? `?${query}` : ""}`);
    },
    [debouncedNavigate, router, searchParams]
  );

  // Xóa tìm kiếm
  const clearSearch = useCallback(() => {
    debouncedNavigate.cancel();
    setInputValue("");
    const params = new URLSearchParams(searchParams.toString());
    params.delete("q");
    const query = params.toString();
    router.push(`/home${query ? `?${query}` : ""}`);
  }, [debouncedNavigate, router, searchParams]);

  // Gọi API search khi có keyword
  const searchQuery = useQuery({
    queryKey: ["searchProducts", keyword],
    queryFn: () => ProductService.search(keyword, 0, 20),
    enabled: !!keyword && keyword.length > 0,
    staleTime: 30 * 1000,
  });

  return {
    keyword,
    inputValue,
    handleSearch,
    handleSearchImmediate,
    clearSearch,
    searchQuery,
    isSearching: !!keyword,
  };
};