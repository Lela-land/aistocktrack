"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsTrigger, TabsList } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import {
  Bell,
  BellRing,
  TrendingDown,
  Globe,
  AlertCircle,
  Menu,
  Home,
  Search,
  ShoppingCart,
  User,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { cn, ApiService, transformBackendProduct, getStockStatusColor, getStockStatusText, type Product as BackendProduct } from "@/lib/utils"

interface Product {
  id: string
  name: string
  series: string
  category: string
  stock: number
  price: number
  image: string
  isHot: boolean
  isTracked: boolean
  originalPrice?: number
  isOnSale?: boolean
  discountPercentage?: number
  description?: string
  purchaseLink?: string
  stockStatus?: string
  lastUpdated?: string
}

export default function MobileApp() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [userAlerts, setUserAlerts] = useState<string[]>([]) // Track which products have alerts

  const [stockChanges, setStockChanges] = useState<{ [key: string]: boolean }>({})
  const [selectedCountry, setSelectedCountry] = useState("US")
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [activeTab, setActiveTab] = useState("home")
  const [currentSlide, setCurrentSlide] = useState(0)
  const [isSheetOpen, setIsSheetOpen] = useState(false)

  const countries = [
    { value: "US", label: "United States", flag: "🇺🇸" },
    { value: "UK", label: "United Kingdom", flag: "🇬🇧" },
    { value: "CA", label: "Canada", flag: "🇨🇦" },
    { value: "AU", label: "Australia", flag: "🇦🇺" },
    { value: "DE", label: "Germany", flag: "🇩🇪" },
    { value: "JP", label: "Japan", flag: "🇯🇵" },
  ]

  // Fetch products from backend API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch Pop Mart products from backend
        const response = await ApiService.getProducts({ 
          brand: 'pop_mart',
          per_page: 50
        })
        
        if (response.success && response.data) {
          // Transform backend products to frontend format
          const transformedProducts = response.data.map(transformBackendProduct)
          setProducts(transformedProducts)
        } else {
          setError(response.error || 'Failed to load products')
        }
      } catch (err) {
        setError('Failed to connect to server')
        console.error('Failed to fetch products:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  // Fetch user alerts to determine tracked products
  useEffect(() => {
    const fetchUserAlerts = async () => {
      try {
        const response = await ApiService.getUserAlerts()
        if (response.success && response.data) {
          const alertProductIds = response.data.map(alert => alert.product_id)
          setUserAlerts(alertProductIds)
          
          // Update product tracking status
          setProducts(prev => prev.map(product => ({
            ...product,
            isTracked: alertProductIds.includes(product.id)
          })))
        }
      } catch (err) {
        console.error('Failed to fetch user alerts:', err)
      }
    }

    if (products.length > 0) {
      fetchUserAlerts()
    }
  }, [products.length])

  // Real-time stock updates
  useEffect(() => {
    if (products.length === 0) return

    const interval = setInterval(async () => {
      try {
        // Refetch products to get updated stock levels
        const response = await ApiService.getProducts({ 
          brand: 'pop_mart',
          per_page: 50
        })
        
        if (response.success && response.data) {
          const transformedProducts = response.data.map(transformBackendProduct)
          
          // Update tracked status based on current user alerts
          const updatedProducts = transformedProducts.map(product => ({
            ...product,
            isTracked: userAlerts.includes(product.id)
          }))
          
          setProducts(prev => {
            // Check for stock changes to show animations
            const changes: { [key: string]: boolean } = {}
            updatedProducts.forEach(newProduct => {
              const oldProduct = prev.find(p => p.id === newProduct.id)
              if (oldProduct && oldProduct.stock !== newProduct.stock) {
                changes[newProduct.id] = true
              }
            })
            setStockChanges(changes)
            
            // Clear stock change animations after 2 seconds
            setTimeout(() => setStockChanges({}), 2000)
            
            return updatedProducts
          })
        }
      } catch (err) {
        console.error('Failed to update stock levels:', err)
      }
    }, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [products.length, userAlerts])

  // 获取被追踪的商品
  const trackedProducts = products.filter((product) => product.isTracked)

  // 切换热门商品的函数
  const switchHotProduct = () => {
    setIsTransitioning(true)

    setTimeout(() => {
      setProducts((prev) => {
        const newProducts = [...prev]
        const currentHotIndex = newProducts.findIndex((p) => p.isHot)
        const availableProducts = newProducts.filter((p) => !p.isHot && p.stock > 0)

        if (availableProducts.length > 0) {
          if (currentHotIndex !== -1) {
            newProducts[currentHotIndex].isHot = false
          }

          const randomIndex = Math.floor(Math.random() * availableProducts.length)
          const newHotProduct = availableProducts[randomIndex]
          const newHotIndex = newProducts.findIndex((p) => p.id === newHotProduct.id)

          if (newHotIndex !== -1) {
            newProducts[newHotIndex].isHot = true
          }
        }

        return newProducts
      })

      setTimeout(() => {
        setIsTransitioning(false)
      }, 500)
    }, 500)
  }

  // 模拟实时库存变化
  useEffect(() => {
    const interval = setInterval(() => {
      setProducts((prev) => {
        const newProducts = [...prev]
        const hotProduct = newProducts.find((p) => p.isHot)

        if (hotProduct && hotProduct.stock > 0 && Math.random() < 0.4) {
          const decrease = Math.floor(Math.random() * 2) + 1
          const newStock = Math.max(0, hotProduct.stock - decrease)
          hotProduct.stock = newStock

          setStockChanges((prev) => ({
            ...prev,
            [hotProduct.id]: true,
          }))

          setTimeout(() => {
            setStockChanges((prev) => ({
              ...prev,
              [hotProduct.id]: false,
            }))
          }, 1500)

          if (newStock === 0) {
            setTimeout(() => {
              switchHotProduct()
            }, 2000)
          }
        }

        return newProducts
      })
    }, 4000)

    return () => clearInterval(interval)
  }, [])

  const toggleTracking = (productId: string) => {
    setProducts((prev) =>
      prev.map((product) => (product.id === productId ? { ...product, isTracked: !product.isTracked } : product)),
    )
  }

  const hotProduct = products.find((p) => p.isHot)
  const categories = ["All", "Labubu", "SKULLPANDA", "dimoo", "crybaby", "others"]
  const [activeCategory, setActiveCategory] = useState("All")

  const eligibleProducts = products.filter((product) => (product.isHot || product.isTracked) && product.stock > 0)

  // 如果当前商品库存为0或不符合条件，自动切换到下一个符合条件的商品
  useEffect(() => {
    const currentProduct = eligibleProducts[currentSlide]
    if (!currentProduct || currentProduct.stock === 0) {
      const nextAvailableIndex = eligibleProducts.findIndex((p, index) => p.stock > 0 && index !== currentSlide)
      if (nextAvailableIndex !== -1) {
        setCurrentSlide(nextAvailableIndex)
      }
    }
  }, [eligibleProducts, currentSlide])

  const nextSlide = () => {
    if (isTransitioning || eligibleProducts.length <= 1) return
    setIsTransitioning(true)
    setCurrentSlide((prev) => (prev + 1) % eligibleProducts.length)
    setTimeout(() => setIsTransitioning(false), 500)
  }

  const prevSlide = () => {
    if (isTransitioning || eligibleProducts.length <= 1) return
    setIsTransitioning(true)
    setCurrentSlide((prev) => (prev - 1 + eligibleProducts.length) % eligibleProducts.length)
    setTimeout(() => setIsTransitioning(false), 500)
  }

  const goToSlide = (index: number) => {
    if (isTransitioning || index === currentSlide) return
    setIsTransitioning(true)
    setCurrentSlide(index)
    setTimeout(() => setIsTransitioning(false), 500)
  }

  const currentProduct = eligibleProducts[currentSlide]

  const filteredProducts =
    activeCategory === "All"
      ? products.filter((p) => !eligibleProducts.some((hp) => hp.id === p.id))
      : products.filter((p) => p.category === activeCategory && !eligibleProducts.some((hp) => hp.id === p.id))

  const getStockStatus = (stock: number) => {
    if (stock === 0) return { text: "Out of Stock", color: "bg-red-500", textColor: "text-red-500" }
    if (stock <= 10) return { text: "Low Stock", color: "bg-orange-500", textColor: "text-orange-500" }
    if (stock <= 20) return { text: "In Stock", color: "bg-yellow-500", textColor: "text-yellow-600" }
    return { text: "In Stock", color: "bg-green-500", textColor: "text-green-600" }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Mobile Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm" className="p-2">
                    <Menu className="w-5 h-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-80">
                  <SheetHeader>
                    <SheetTitle className="flex items-center gap-2">
                      <img src="/images/popmart-logo.png" alt="POP MART" className="h-6 w-auto" />
                    </SheetTitle>
                  </SheetHeader>
                  <div className="mt-6 space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Country/Region</label>
                      <Select value={selectedCountry} onValueChange={setSelectedCountry}>
                        <SelectTrigger className="w-full">
                          <Globe className="w-4 h-4 mr-2" />
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {countries.map((country) => (
                            <SelectItem key={country.value} value={country.value}>
                              <span className="flex items-center gap-2">
                                <span>{country.flag}</span>
                                <span>{country.label}</span>
                              </span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="pt-4 border-t">
                      <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-600" />
                        My Alert List ({trackedProducts.length})
                      </h3>
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {trackedProducts.length === 0 ? (
                          <div className="text-center text-gray-500 py-8">
                            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                            <p className="text-sm">No items being tracked</p>
                          </div>
                        ) : (
                          trackedProducts.map((product) => {
                            const stockStatus = getStockStatus(product.stock)
                            return (
                              <div key={product.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                <img
                                  src={product.image || "/placeholder.svg"}
                                  alt={product.name}
                                  className="w-12 h-12 object-cover rounded-lg"
                                />
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-sm font-medium text-gray-900 truncate">{product.name}</h4>
                                  <div className="flex items-center gap-2 mt-1">
                                    <span className="text-sm font-bold text-red-600">¥{product.price}</span>
                                    <Badge variant="outline" className={cn("text-xs", stockStatus.textColor)}>
                                      {product.stock}
                                    </Badge>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => toggleTracking(product.id)}
                                  className="text-red-600 p-2"
                                >
                                  <BellRing className="w-4 h-4" />
                                </Button>
                              </div>
                            )
                          })
                        )}
                      </div>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>

              <img src="/images/popmart-logo.png" alt="POP MART" className="h-6 w-auto" />
              <div className="text-xs text-gray-600 font-medium">RESTOCK ALERTS</div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSheetOpen(true)}
                className="flex items-center gap-1 hover:text-red-600 transition-colors relative p-2"
              >
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-medium">Alert</span>
                {trackedProducts.length > 0 && (
                  <Badge className="bg-red-600 text-white text-xs px-1 py-0 h-4 min-w-4 rounded-full absolute -top-1 -right-1">
                    {trackedProducts.length}
                  </Badge>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Banner Area - 类似web版轮播 */}
      {eligibleProducts.length > 0 && currentProduct && (
        <section className="px-4 py-6">
          <div
            className={cn(
              "relative overflow-hidden shadow-xl transition-all duration-1000 rounded-3xl",
              isTransitioning && "scale-95 opacity-80",
            )}
            style={{
              height: "500px", // 增加高度以占满竖屏
            }}
          >
            {/* 背景图片 - 固定森林背景 */}
            <div className="absolute inset-0 z-0">
              <img
                src="/images/labubu-forest-bg.png"
                alt=""
                className="w-full h-full object-cover opacity-15 blur-sm scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-br from-white/80 via-white/60 to-white/80" />
            </div>

            {/* 背景装饰圆圈 */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-12 left-12 w-24 h-24 bg-red-500 rounded-full blur-3xl animate-pulse" />
              <div
                className="absolute bottom-12 right-12 w-28 h-28 bg-blue-500 rounded-full blur-3xl animate-pulse"
                style={{ animationDelay: "1s" }}
              />
              <div
                className="absolute top-1/3 right-8 w-20 h-20 bg-yellow-500 rounded-full blur-3xl animate-pulse"
                style={{ animationDelay: "2s" }}
              />
            </div>

            {/* 主要内容区域 - 竖版布局 */}
            <div className="relative z-10 h-full flex flex-col">
              {/* 上半部分：商品展示 */}
              <div className="flex-1 flex flex-col items-center justify-center relative">
                {/* 商品状态提示 - 移到图片上方，移除LIVE标签 */}
                <div className="flex items-center justify-center gap-3 mb-6">
                  <Badge className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 text-sm font-bold rounded-full">
                    {currentProduct.isHot ? "🔥 HOT ITEM" : "🔔 TRACKED"}
                  </Badge>
                  <Badge variant="outline" className="px-4 py-2 text-sm font-bold rounded-full border-2">
                    {currentProduct.series}
                  </Badge>
                </div>

                {/* 商品图片 - 移除圆形背景 */}
                <div
                  className={cn(
                    "relative transition-all duration-500 transform",
                    isTransitioning && "opacity-0 scale-95 rotate-3",
                  )}
                >
                  <div className="relative z-10 w-48 h-48 flex items-center justify-center">
                    <img
                      src={currentProduct.image || "/placeholder.svg?height=180&width=180"}
                      alt={currentProduct.name}
                      className="w-40 h-40 object-contain drop-shadow-2xl"
                      style={{
                        filter: "drop-shadow(0 20px 40px rgba(0,0,0,0.3))",
                      }}
                      onError={(e) => {
                        e.currentTarget.src =
                          "/placeholder.svg?height=180&width=180&text=" + encodeURIComponent(currentProduct.name)
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* 下半部分：商品信息 */}
              <div className="px-6 pb-8 space-y-4">
                {/* 商品名称 */}
                <h1
                  className={cn(
                    "text-xl font-bold text-gray-900 leading-tight text-center transition-all duration-500",
                    isTransitioning && "opacity-0 translate-y-4",
                  )}
                >
                  {currentProduct.name}
                </h1>

                {/* 价格和库存 */}
                <div className="flex items-center justify-center gap-8">
                  <div className="text-center space-y-1">
                    <p className="text-sm text-gray-600 font-medium">Price</p>
                    <div
                      className={cn(
                        "text-3xl font-bold text-red-600 transition-all duration-500",
                        isTransitioning && "opacity-0 scale-95",
                      )}
                    >
                      ¥{currentProduct.price}
                    </div>
                  </div>

                  <div className="text-center space-y-1">
                    <p className="text-sm text-gray-600 font-medium">Stock</p>
                    <div
                      className={cn(
                        "text-3xl font-bold font-mono transition-all duration-500",
                        stockChanges[currentProduct.id]
                          ? "text-red-500 animate-pulse scale-110"
                          : currentProduct.stock <= 10
                            ? "text-orange-500"
                            : "text-green-500",
                        isTransitioning && "opacity-0 scale-95",
                      )}
                      style={{
                        textShadow: stockChanges[currentProduct.id]
                          ? "0 0 20px rgba(255,0,0,0.5)"
                          : "0 0 10px rgba(0,0,0,0.1)",
                      }}
                    >
                      {currentProduct.stock.toString().padStart(2, "0")}
                    </div>

                    {stockChanges[currentProduct.id] && (
                      <div className="flex items-center justify-center gap-1 text-red-500 animate-bounce">
                        <TrendingDown className="w-4 h-4" />
                        <span className="font-bold text-sm">DECREASING</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* 操作按钮 - 缩小尺寸，增加底部间距 */}
                <div className="flex items-center justify-center gap-3 pt-4 pb-4">
                  <Button
                    size="sm"
                    className={cn(
                      "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
                      "text-white font-bold text-xs px-4 py-2 rounded-full transition-all duration-300",
                      "hover:scale-105 hover:shadow-lg transform",
                      isTransitioning && "opacity-0 translate-y-4",
                    )}
                  >
                    <ShoppingCart className="w-3 h-3 mr-2" />
                    Add to Cart
                  </Button>

                  <Button
                    onClick={() => toggleTracking(currentProduct.id)}
                    size="sm"
                    variant="outline"
                    className={cn(
                      "font-bold text-xs px-4 py-2 rounded-full transition-all duration-300 border-2",
                      "hover:scale-105 hover:shadow-lg transform",
                      currentProduct.isTracked
                        ? "bg-green-50 border-green-500 text-green-600 hover:bg-green-100"
                        : "border-red-500 text-red-600 hover:bg-red-50",
                      isTransitioning && "opacity-0 translate-y-4",
                    )}
                  >
                    {currentProduct.isTracked ? (
                      <>
                        <BellRing className="w-3 h-3 mr-2" />
                        Tracking
                      </>
                    ) : (
                      <>
                        <Bell className="w-3 h-3 mr-2" />
                        Track Stock
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* 导航控制 */}
            {eligibleProducts.length > 1 && (
              <>
                <div className="absolute inset-y-0 left-2 flex items-center z-20">
                  <Button
                    onClick={prevSlide}
                    variant="ghost"
                    size="sm"
                    className="w-10 h-10 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white/90 shadow-lg transition-all duration-300 hover:scale-110"
                    disabled={isTransitioning}
                  >
                    <ChevronLeft className="w-5 h-5 text-gray-700" />
                  </Button>
                </div>

                <div className="absolute inset-y-0 right-2 flex items-center z-20">
                  <Button
                    onClick={nextSlide}
                    variant="ghost"
                    size="sm"
                    className="w-10 h-10 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white/90 shadow-lg transition-all duration-300 hover:scale-110"
                    disabled={isTransitioning}
                  >
                    <ChevronRight className="w-5 h-5 text-gray-700" />
                  </Button>
                </div>

                {/* 底部指示器 - 调整位置避免与按钮重叠 */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20">
                  <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
                    {eligibleProducts.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => goToSlide(index)}
                        className={cn(
                          "w-2.5 h-2.5 rounded-full transition-all duration-300",
                          index === currentSlide
                            ? "bg-red-500 scale-125"
                            : "bg-gray-300 hover:bg-gray-400 hover:scale-110",
                        )}
                        disabled={isTransitioning}
                      />
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </section>
      )}

      {/* Mobile Product Categories */}
      <section className="px-4 pb-6">
        <Tabs value={activeCategory} onValueChange={setActiveCategory} className="w-full">
          <div className="mb-6">
            <TabsList className="flex flex-wrap justify-center gap-3 bg-transparent">
              {categories.map((category, index) => {
                const icons = ["🌟", "⭐", "💀", "⚡", "💖", "🎯"]
                return (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className={cn(
                      "text-sm font-bold transition-all duration-300 rounded-full px-6 py-3 border-2",
                      "hover:scale-105 hover:-translate-y-1 hover:shadow-lg",
                      "data-[state=active]:bg-gradient-to-r data-[state=active]:from-red-500 data-[state=active]:to-red-600",
                      "data-[state=active]:text-white data-[state=active]:shadow-xl data-[state=active]:scale-105 data-[state=active]:border-red-500",
                      "data-[state=inactive]:bg-white data-[state=inactive]:text-gray-700 data-[state=inactive]:shadow-md data-[state=inactive]:border-gray-200",
                      "data-[state=inactive]:hover:bg-gradient-to-r data-[state=inactive]:hover:from-gray-100 data-[state=inactive]:hover:to-gray-200",
                    )}
                  >
                    <span className="mr-2 text-base">{icons[index] || "🎯"}</span>
                    {category}
                  </TabsTrigger>
                )
              })}
            </TabsList>
          </div>

          <div className="grid grid-cols-1 gap-4 mt-4">
            {filteredProducts.map((product) => {
              const stockStatus = getStockStatus(product.stock)

              return (
                <Card key={product.id} className="hover:shadow-lg transition-all duration-300 border-gray-200">
                  <div className="flex items-center p-4 gap-4">
                    {/* 商品图片 */}
                    <div className="w-20 h-20 rounded-lg overflow-hidden bg-gray-50 flex-shrink-0">
                      <img
                        src={product.image || "/placeholder.svg"}
                        alt={product.name}
                        className="w-full h-full object-cover"
                      />
                    </div>

                    {/* 商品信息 */}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-bold text-gray-900 line-clamp-2 mb-1">{product.name}</h3>
                      <p className="text-xs text-gray-600 mb-2">{product.series}</p>

                      <div className="flex items-center justify-between mb-3">
                        <span className="text-lg font-bold text-red-600">¥{product.price}</span>
                        <Badge variant="outline" className={cn("text-xs", stockStatus.textColor)}>
                          {product.stock}
                        </Badge>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          onClick={() => toggleTracking(product.id)}
                          size="sm"
                          className={cn(
                            "text-xs font-medium h-8 flex-1",
                            product.isTracked
                              ? "bg-green-600 hover:bg-green-700 text-white"
                              : "bg-red-600 hover:bg-red-700 text-white",
                          )}
                        >
                          {product.isTracked ? (
                            <>
                              <BellRing className="w-3 h-3 mr-1" />
                              Tracking
                            </>
                          ) : (
                            <>
                              <Bell className="w-3 h-3 mr-1" />
                              ALERT
                            </>
                          )}
                        </Button>
                        <Button
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium h-8 flex-1"
                        >
                          <ShoppingCart className="w-3 h-3 mr-1" />
                          Add to Cart
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        </Tabs>
      </section>

      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 z-50">
        <div className="flex justify-around items-center">
          <button
            onClick={() => setActiveTab("home")}
            className={cn(
              "flex flex-col items-center gap-1 p-2 rounded-lg transition-colors",
              activeTab === "home" ? "text-red-600 bg-red-50" : "text-gray-600",
            )}
          >
            <Home className="w-5 h-5" />
            <span className="text-xs font-medium">Home</span>
          </button>

          <button
            onClick={() => setActiveTab("search")}
            className={cn(
              "flex flex-col items-center gap-1 p-2 rounded-lg transition-colors",
              activeTab === "search" ? "text-red-600 bg-red-50" : "text-gray-600",
            )}
          >
            <Search className="w-5 h-5" />
            <span className="text-xs font-medium">Search</span>
          </button>

          <button
            onClick={() => setActiveTab("alerts")}
            className={cn(
              "flex flex-col items-center gap-1 p-2 rounded-lg transition-colors relative",
              activeTab === "alerts" ? "text-red-600 bg-red-50" : "text-gray-600",
            )}
          >
            <AlertCircle className="w-5 h-5" />
            <span className="text-xs font-medium">Alerts</span>
            {trackedProducts.length > 0 && (
              <Badge className="absolute -top-1 -right-1 bg-red-600 text-white text-xs px-1 py-0 h-4 min-w-4 rounded-full">
                {trackedProducts.length}
              </Badge>
            )}
          </button>

          <button
            onClick={() => setActiveTab("cart")}
            className={cn(
              "flex flex-col items-center gap-1 p-2 rounded-lg transition-colors",
              activeTab === "cart" ? "text-red-600 bg-red-50" : "text-gray-600",
            )}
          >
            <ShoppingCart className="w-5 h-5" />
            <span className="text-xs font-medium">Cart</span>
          </button>

          <button
            onClick={() => setActiveTab("profile")}
            className={cn(
              "flex flex-col items-center gap-1 p-2 rounded-lg transition-colors",
              activeTab === "profile" ? "text-red-600 bg-red-50" : "text-gray-600",
            )}
          >
            <User className="w-5 h-5" />
            <span className="text-xs font-medium">Profile</span>
          </button>
        </div>
      </div>
    </div>
  )
}
