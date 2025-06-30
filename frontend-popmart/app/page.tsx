"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Smartphone, Monitor, Eye } from "lucide-react"
import Component from "../popmart-monitor"
import MobileApp from "../app-mobile"

export default function Page() {
  const [viewMode, setViewMode] = useState<"desktop" | "mobile" | "preview">("desktop")

  return (
    <div className="min-h-screen">
      {/* 版本切换按钮 */}
      <div className="fixed top-4 right-4 z-50 flex gap-2">
        <Button
          onClick={() => setViewMode("desktop")}
          variant={viewMode === "desktop" ? "default" : "outline"}
          size="sm"
          className="rounded-full"
        >
          <Monitor className="w-4 h-4 mr-2" />
          Desktop
        </Button>
        <Button
          onClick={() => setViewMode("mobile")}
          variant={viewMode === "mobile" ? "default" : "outline"}
          size="sm"
          className="rounded-full"
        >
          <Smartphone className="w-4 h-4 mr-2" />
          Mobile
        </Button>
        <Button
          onClick={() => setViewMode("preview")}
          variant={viewMode === "preview" ? "default" : "outline"}
          size="sm"
          className="rounded-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-0"
        >
          <Eye className="w-4 h-4 mr-2" />
          App Preview
        </Button>
      </div>

      {/* 根据选择显示不同版本 */}
      {viewMode === "desktop" ? (
        <Component />
      ) : viewMode === "mobile" ? (
        <div className="max-w-sm mx-auto bg-gray-100 min-h-screen">
          <MobileApp />
        </div>
      ) : (
        // App Preview 模式
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-pink-900 flex items-center justify-center p-8">
          <div className="relative">
            {/* 手机外框 */}
            <div className="relative bg-black rounded-[3rem] p-2 shadow-2xl">
              <div className="bg-gray-900 rounded-[2.5rem] p-1">
                <div className="bg-white rounded-[2rem] overflow-hidden w-80 h-[640px] relative">
                  {/* 手机状态栏 */}
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-black rounded-b-xl z-50"></div>

                  {/* App 内容 */}
                  <div className="w-full h-full overflow-hidden">
                    <MobileApp />
                  </div>
                </div>
              </div>
            </div>

            {/* 装饰效果 */}
            <div className="absolute -inset-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-[4rem] blur-xl"></div>
            <div className="absolute -inset-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-[5rem] blur-2xl"></div>

            {/* 标题 */}
            <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 text-center">
              <h2 className="text-2xl font-bold text-white mb-2">POP MART Restock Alerts</h2>
              <p className="text-gray-300 text-sm">Mobile App Preview</p>
            </div>
          </div>

          {/* 背景装饰 */}
          <div className="absolute top-20 left-20 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div
            className="absolute bottom-20 right-20 w-40 h-40 bg-pink-500/20 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "1s" }}
          ></div>
          <div
            className="absolute top-1/2 left-10 w-24 h-24 bg-blue-500/20 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "2s" }}
          ></div>
        </div>
      )}
    </div>
  )
}
