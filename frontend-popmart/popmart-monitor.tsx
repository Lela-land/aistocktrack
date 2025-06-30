"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Bell, BellRing, TrendingDown, Globe, AlertCircle, ShoppingCart, ChevronLeft, ChevronRight } from "lucide-react"
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

export default function Component() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [userAlerts, setUserAlerts] = useState<string[]>([]) // Track which products have alerts

  const [stockChanges, setStockChanges] = useState<{ [key: string]: boolean }>({})
  const [selectedCountry, setSelectedCountry] = useState("US")
  const [currentSlide, setCurrentSlide] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)

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

  // Real-time stock updates simulation (replace with WebSocket in production)
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

  // 获取符合条件的商品：热门商品或被追踪的商品，且有库存
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

  // 模拟实时库存变化
  useEffect(() => {
    const interval = setInterval(() => {
      setProducts((prev) => {
        const newProducts = [...prev]
        const currentProduct = eligibleProducts[currentSlide]

        if (currentProduct && currentProduct.stock > 0 && Math.random() < 0.3) {
          const productIndex = newProducts.findIndex((p) => p.id === currentProduct.id)
          if (productIndex !== -1) {
            const decrease = Math.floor(Math.random() * 2) + 1
            const newStock = Math.max(0, newProducts[productIndex].stock - decrease)
            newProducts[productIndex].stock = newStock

            // 触发动画效果
            setStockChanges((prev) => ({
              ...prev,
              [currentProduct.id]: true,
            }))

            setTimeout(() => {
              setStockChanges((prev) => ({
                ...prev,
                [currentProduct.id]: false,
              }))
            }, 1500)

            // 如果库存为0，自动切换到下一个有库存的商品
            if (newStock === 0) {
              setTimeout(() => {
                const remainingProducts = newProducts.filter(
                  (p) => (p.isHot || p.isTracked) && p.stock > 0 && p.id !== currentProduct.id,
                )
                if (remainingProducts.length > 0) {
                  // 切换到下一个有库存的商品
                  const nextProductIndex = newProducts.findIndex((p) => p.id === remainingProducts[0].id)
                  const nextSlideIndex = eligibleProducts.findIndex((p) => p.id === remainingProducts[0].id)
                  if (nextSlideIndex !== -1) {
                    setCurrentSlide(nextSlideIndex)
                  }
                }
              }, 2000)
            }
          }
        }

        return newProducts
      })
    }, 4000)

    return () => clearInterval(interval)
  }, [currentSlide, eligibleProducts])

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

  const toggleTracking = async (productId: string) => {
    const product = products.find(p => p.id === productId)
    if (!product) return

    try {
      if (product.isTracked) {
        // Remove alert - find the alert ID and delete it
        const response = await ApiService.getUserAlerts()
        if (response.success && response.data) {
          const alert = response.data.find(a => a.product_id === productId)
          if (alert && alert.id) {
            await ApiService.deleteStockAlert(alert.id)
          }
        }
        
        // Update local state
        setUserAlerts(prev => prev.filter(id => id !== productId))
        setProducts(prev => 
          prev.map(p => p.id === productId ? { ...p, isTracked: false } : p)
        )
      } else {
        // Create new alert
        const alertResponse = await ApiService.createStockAlert({
          product_id: productId,
          alert_type: 'restock'
        })
        
        if (alertResponse.success) {
          // Update local state
          setUserAlerts(prev => [...prev, productId])
          setProducts(prev => 
            prev.map(p => p.id === productId ? { ...p, isTracked: true } : p)
          )
        }
      }
    } catch (err) {
      console.error('Failed to toggle tracking:', err)
      // Could show error toast here
    }
  }

  const categories = ["All", "Labubu", "SKULLPANDA", "dimoo", "crybaby", "others"]
  const [activeCategory, setActiveCategory] = useState("All")

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

  const currentProduct = eligibleProducts[currentSlide]

  return (
    <div className="min-h-screen bg-white">
      {/* Header - POP MART Style */}
      <header className="bg-white shadow-sm border-b relative z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <img src="/images/popmart-logo.png" alt="POP MART" className="h-8 w-auto" />
              <div className="text-sm text-gray-600 font-medium">RESTOCK ALERTS</div>
            </div>
            <div className="flex items-center gap-6 text-sm font-medium text-gray-700">
              {/* My Alert 弹出菜单 */}
              <Popover>
                <PopoverTrigger asChild>
                  <button className="flex items-center gap-1 hover:text-red-600 transition-colors relative">
                    <AlertCircle className="w-4 h-4" />
                    <span>My Alert</span>
                    {trackedProducts.length > 0 && (
                      <Badge className="bg-red-600 text-white text-xs px-1 py-0 h-4 min-w-4 rounded-full absolute -top-2 -right-2">
                        {trackedProducts.length}
                      </Badge>
                    )}
                  </button>
                </PopoverTrigger>
                <PopoverContent
                  className="w-96 p-0 rounded-3xl shadow-2xl border-2 border-gray-100 bg-gradient-to-br from-white to-gray-50"
                  align="end"
                >
                  <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-red-50 to-pink-50 rounded-t-3xl">
                    <h3 className="font-bold text-gray-900 flex items-center gap-3 text-lg">
                      <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center">
                        <AlertCircle className="w-4 h-4 text-white" />
                      </div>
                      My Alert List ({trackedProducts.length})
                    </h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {trackedProducts.length === 0 ? (
                      <div className="p-8 text-center text-gray-500">
                        <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                          <AlertCircle className="w-8 h-8 text-gray-300" />
                        </div>
                        <p className="text-lg font-medium">No items being tracked</p>
                        <p className="text-sm text-gray-400 mt-2">Click ALERT button on products to track them</p>
                      </div>
                    ) : (
                      <div className="p-3">
                        {trackedProducts.map((product) => {
                          const stockStatus = getStockStatus(product.stock)
                          return (
                            <div
                              key={product.id}
                              className={cn(
                                "flex items-center gap-4 p-4 hover:bg-gradient-to-r hover:from-red-50 hover:to-pink-50",
                                "rounded-2xl border border-transparent hover:border-red-100 transition-all duration-300",
                                "hover:scale-102 hover:shadow-lg mb-2",
                              )}
                            >
                              <div className="relative">
                                <img
                                  src={product.image || "/placeholder.svg"}
                                  alt={product.name}
                                  className="w-16 h-16 object-cover rounded-2xl bg-gray-100 shadow-md"
                                />
                                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-green-400 to-green-500 rounded-full border-2 border-white" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h4 className="text-sm font-bold text-gray-900 truncate">{product.name}</h4>
                                <p className="text-xs text-gray-500 font-medium">{product.series}</p>
                                <div className="flex items-center gap-3 mt-2">
                                  <span className="text-lg font-bold text-red-600">¥{product.price}</span>
                                  <Badge
                                    variant="outline"
                                    className={cn("text-xs font-bold px-2 py-1 rounded-full", stockStatus.textColor)}
                                  >
                                    {product.stock}
                                  </Badge>
                                </div>
                              </div>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => toggleTracking(product.id)}
                                className={cn(
                                  "text-red-600 hover:text-red-700 hover:bg-red-50 rounded-full p-3",
                                  "transition-all duration-300 hover:scale-110 hover:shadow-lg",
                                )}
                              >
                                <BellRing className="w-5 h-5" />
                              </Button>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </PopoverContent>
              </Popover>

              {/* 国家选择下拉菜单 */}
              <Select value={selectedCountry} onValueChange={setSelectedCountry}>
                <SelectTrigger className="w-40 h-8 text-xs">
                  <Globe className="w-3 h-3 mr-1" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {countries.map((country) => (
                    <SelectItem key={country.value} value={country.value} className="text-xs">
                      <span className="flex items-center gap-2">
                        <span>{country.flag}</span>
                        <span>{country.label}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                LIVE
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Loading State */}
      {loading && (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-50">
          <div className="text-center space-y-6">
            <div className="w-16 h-16 mx-auto bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center animate-pulse">
              <AlertCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Loading Pop Mart Products...</h2>
            <p className="text-gray-600">Connecting to inventory system</p>
            <div className="flex justify-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-50">
          <div className="text-center space-y-6 max-w-md mx-auto p-8">
            <div className="w-16 h-16 mx-auto bg-red-500 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Connection Error</h2>
            <p className="text-gray-600">{error}</p>
            <Button 
              onClick={() => window.location.reload()} 
              className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold px-6 py-3 rounded-full"
            >
              Retry Connection
            </Button>
          </div>
        </div>
      )}

      {/* No Products State */}
      {!loading && !error && products.length === 0 && (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-50">
          <div className="text-center space-y-6 max-w-md mx-auto p-8">
            <div className="w-16 h-16 mx-auto bg-gray-400 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">No Products Found</h2>
            <p className="text-gray-600">No Pop Mart products are currently available for monitoring.</p>
          </div>
        </div>
      )}

      {/* 全屏轮播Banner */}
      {!loading && !error && eligibleProducts.length > 0 && currentProduct && (
        <section className="relative h-[70vh] overflow-hidden">
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
            <div className="absolute top-20 left-20 w-32 h-32 bg-red-500 rounded-full blur-3xl animate-pulse" />
            <div
              className="absolute bottom-20 right-20 w-40 h-40 bg-blue-500 rounded-full blur-3xl animate-pulse"
              style={{ animationDelay: "1s" }}
            />
            <div
              className="absolute top-1/2 left-1/4 w-24 h-24 bg-yellow-500 rounded-full blur-3xl animate-pulse"
              style={{ animationDelay: "2s" }}
            />
          </div>

          {/* 主要内容区域 */}
          <div className="relative z-10 h-full flex items-center">
            <div className="container mx-auto px-8">
              <div className="grid grid-cols-12 gap-12 items-center h-full">
                {/* 左侧：商品信息 */}
                <div className="col-span-6 space-y-6">
                  {/* 商品状态提示 */}
                  <div className="flex items-center gap-4 mb-4">
                    <Badge className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 text-sm font-bold rounded-full">
                      {currentProduct.isHot ? "🔥 HOT ITEM" : "🔔 TRACKED ITEM"}
                    </Badge>
                    <Badge variant="outline" className="px-4 py-2 text-sm font-bold rounded-full border-2">
                      {currentProduct.series}
                    </Badge>
                    <Badge className="bg-green-500 text-white px-3 py-1 text-xs font-bold rounded-full">
                      LIVE MONITORING
                    </Badge>
                  </div>

                  {/* 商品名称 */}
                  <div className="space-y-4">
                    <h1
                      className={cn(
                        "text-4xl font-bold text-gray-900 leading-tight transition-all duration-500",
                        isTransitioning && "opacity-0 translate-x-8",
                      )}
                    >
                      {currentProduct.name}
                    </h1>
                  </div>

                  {/* 价格和库存 */}
                  <div className="flex items-center gap-8">
                    <div className="space-y-2">
                      <p className="text-lg text-gray-600 font-medium">Price</p>
                      <div
                        className={cn(
                          "text-5xl font-bold text-red-600 transition-all duration-500",
                          isTransitioning && "opacity-0 scale-95",
                        )}
                      >
                        ¥{currentProduct.price}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p className="text-lg text-gray-600 font-medium">Stock</p>
                      <div
                        className={cn(
                          "text-5xl font-bold font-mono transition-all duration-500",
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
                        <div className="flex items-center gap-2 text-red-500 animate-bounce">
                          <TrendingDown className="w-5 h-5" />
                          <span className="font-bold text-sm">STOCK DECREASING</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-6 pt-4">
                    <Button
                      size="lg"
                      className={cn(
                        "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
                        "text-white font-bold text-lg px-8 py-4 rounded-full transition-all duration-300",
                        "hover:scale-105 hover:shadow-2xl transform",
                        isTransitioning && "opacity-0 translate-y-4",
                      )}
                    >
                      <ShoppingCart className="w-6 h-6 mr-3" />
                      Add to Cart
                    </Button>

                    <Button
                      onClick={() => toggleTracking(currentProduct.id)}
                      size="lg"
                      variant="outline"
                      className={cn(
                        "font-bold text-lg px-8 py-4 rounded-full transition-all duration-300 border-2",
                        "hover:scale-105 hover:shadow-lg transform",
                        currentProduct.isTracked
                          ? "bg-green-50 border-green-500 text-green-600 hover:bg-green-100"
                          : "border-red-500 text-red-600 hover:bg-red-50",
                        isTransitioning && "opacity-0 translate-y-4",
                      )}
                    >
                      {currentProduct.isTracked ? (
                        <>
                          <BellRing className="w-6 h-6 mr-3" />
                          Tracking
                        </>
                      ) : (
                        <>
                          <Bell className="w-6 h-6 mr-3" />
                          Track Stock
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {/* 右侧：商品展示 */}
                <div className="col-span-6 relative flex justify-center items-center">
                  <div
                    className={cn(
                      "relative transition-all duration-500 transform",
                      isTransitioning && "opacity-0 scale-95 rotate-3",
                    )}
                  >
                    {/* 装饰性背景圆圈 */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-104 h-104 bg-gradient-to-br from-red-100 to-pink-100 rounded-full opacity-50 animate-pulse" />
                    <div
                      className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-125 h-125 bg-gradient-to-tl from-blue-100 to-purple-100 rounded-full opacity-30 animate-pulse"
                      style={{ animationDelay: "1s" }}
                    />

                    {/* 商品图片 */}
                    <div className="relative z-10 w-125 h-125 flex items-center justify-center">
                      <div className="relative">
                        <img
                          src={currentProduct.image || "/placeholder.svg?height=500&width=500"}
                          alt={currentProduct.name}
                          className="w-104 h-104 object-contain drop-shadow-2xl"
                          style={{
                            filter: "drop-shadow(0 20px 40px rgba(0,0,0,0.3))",
                          }}
                          onError={(e) => {
                            e.currentTarget.src =
                              "/placeholder.svg?height=500&width=500&text=" + encodeURIComponent(currentProduct.name)
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 导航控制 */}
          <div className="absolute inset-y-0 left-8 flex items-center z-20">
            <Button
              onClick={prevSlide}
              variant="ghost"
              size="lg"
              className="w-16 h-16 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white/90 shadow-lg transition-all duration-300 hover:scale-110"
              disabled={isTransitioning}
            >
              <ChevronLeft className="w-8 h-8 text-gray-700" />
            </Button>
          </div>

          <div className="absolute inset-y-0 right-8 flex items-center z-20">
            <Button
              onClick={nextSlide}
              variant="ghost"
              size="lg"
              className="w-16 h-16 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white/90 shadow-lg transition-all duration-300 hover:scale-110"
              disabled={isTransitioning}
            >
              <ChevronRight className="w-8 h-8 text-gray-700" />
            </Button>
          </div>

          {/* 底部指示器 */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20">
            {eligibleProducts.length > 1 && (
              <div className="flex items-center gap-3 bg-white/80 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
                {eligibleProducts.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => goToSlide(index)}
                    className={cn(
                      "w-3 h-3 rounded-full transition-all duration-300",
                      index === currentSlide ? "bg-red-500 scale-125" : "bg-gray-300 hover:bg-gray-400 hover:scale-110",
                    )}
                    disabled={isTransitioning}
                  />
                ))}
              </div>
            )}
          </div>
        </section>
      )}

      {/* 商品分类区域 */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <Tabs value={activeCategory} onValueChange={setActiveCategory} className="w-full">
            <div className="flex justify-center mb-12">
              <TabsList className="flex gap-4 bg-transparent h-auto p-0">
                {categories.map((category, index) => {
                  const icons = ["🌟", "⭐", "💀", "⚡", "💖", "🎯"]
                  return (
                    <TabsTrigger
                      key={category}
                      value={category}
                      className={cn(
                        "text-lg font-bold transition-all duration-300 rounded-full px-8 py-4",
                        "hover:scale-105 hover:-translate-y-1 hover:shadow-lg",
                        "data-[state=active]:bg-gradient-to-r data-[state=active]:from-red-500 data-[state=active]:to-red-600",
                        "data-[state=active]:text-white data-[state=active]:shadow-xl data-[state=active]:scale-105",
                        "data-[state=inactive]:bg-white data-[state=inactive]:text-gray-700 data-[state=inactive]:shadow-md data-[state=inactive]:border-2 data-[state=inactive]:border-gray-200",
                        "data-[state=inactive]:hover:bg-gradient-to-r data-[state=inactive]:hover:from-gray-100 data-[state=inactive]:hover:to-gray-200",
                      )}
                    >
                      <span className="mr-3 text-xl">{icons[index] || "🎯"}</span>
                      {category}
                    </TabsTrigger>
                  )
                })}
              </TabsList>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {filteredProducts.map((product) => {
                const stockStatus = getStockStatus(product.stock)

                return (
                  <Card
                    key={product.id}
                    className={cn(
                      "group relative overflow-hidden transition-all duration-500 border-2 border-gray-100",
                      "hover:scale-105 hover:-translate-y-3 hover:rotate-1 hover:shadow-2xl hover:border-red-200",
                      "rounded-[2rem] bg-gradient-to-br from-white to-gray-50",
                      "hover:bg-gradient-to-br hover:from-red-50 hover:to-pink-50",
                    )}
                    style={{
                      boxShadow: "0 10px 25px rgba(0,0,0,0.1), 0 5px 10px rgba(0,0,0,0.05)",
                    }}
                  >
                    <CardHeader className="pb-3 p-4">
                      <div className="aspect-square rounded-[1.5rem] overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 mb-4 relative group-hover:shadow-inner">
                        {/* TRENDING 标签 */}
                        {product.stock <= 10 && (
                          <div className="absolute top-2 left-2 z-10">
                            <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-bold text-xs px-3 py-1 rounded-full shadow-lg">
                              🔥 TRENDING
                            </Badge>
                          </div>
                        )}

                        <img
                          src={product.image || "/placeholder.svg"}
                          alt={product.name}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />

                        {/* 图片遮罩效果 */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      </div>

                      <CardTitle className="text-lg leading-tight text-gray-900 group-hover:text-red-600 transition-colors duration-300 font-bold">
                        {product.name}
                      </CardTitle>
                      <p className="text-sm text-gray-600 font-medium">{product.series}</p>
                    </CardHeader>

                    <CardContent className="pt-0 p-4">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold text-red-600 group-hover:text-red-700 transition-colors">
                            ¥{product.price}
                          </span>
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-sm font-bold px-3 py-1 rounded-full border-2 transition-all duration-300",
                              stockStatus.textColor,
                              "group-hover:scale-110",
                            )}
                          >
                            {product.stock <= 3 ? `Only ${product.stock} left!` : `${product.stock} in stock`}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <Button
                            onClick={() => toggleTracking(product.id)}
                            className={cn(
                              "font-bold text-sm rounded-full transition-all duration-300 shadow-lg",
                              "hover:scale-105 hover:-translate-y-1 hover:shadow-xl",
                              product.isTracked
                                ? "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white"
                                : "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white",
                            )}
                          >
                            {product.isTracked ? (
                              <>
                                <BellRing className="w-4 h-4 mr-2" />
                                ALERT
                              </>
                            ) : (
                              <>
                                <Bell className="w-4 h-4 mr-2" />
                                ALERT
                              </>
                            )}
                          </Button>

                          <Button
                            className={cn(
                              "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
                              "text-white font-bold text-sm rounded-full transition-all duration-300 shadow-lg",
                              "hover:scale-105 hover:-translate-y-1 hover:shadow-xl",
                            )}
                          >
                            <ShoppingCart className="w-4 h-4 mr-2" />
                            Add to Cart
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </Tabs>
        </div>
      </section>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
        }
        
        @keyframes shadowFloat {
          0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.2; }
          50% { transform: translateX(-50%) scale(0.8); opacity: 0.1; }
        }
      `}</style>
    </div>
  )
}
