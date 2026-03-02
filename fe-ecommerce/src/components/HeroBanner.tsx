'use client'
import { Carousel } from 'antd'
import Image from 'next/image'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useRef } from 'react'
import type { CarouselRef } from 'antd/es/carousel'
const bannerImages = [
  { src: '/download.jpg', alt: 'Banner 1' },
  { src: '/download (1).jpg', alt: 'Banner 2' },
  { src: '/download (2).jpg', alt: 'Banner 3' },
]

const sideImages = [
  { src: '/denim patchwork flower vest.jpg', alt: 'Denim Patchwork Flower Vest' },
  { src: '/ig_ mariexevv_handmade.jpg', alt: 'Handmade Collection' },
]

export default function HeroBanner() {
  const carouselRef = useRef<CarouselRef>(null)

  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 pb-2">
      {/* Main Banner Section */}
          <div className="flex gap-4 mb-6">
        {/* Carousel - Main Banner */}
              <div className="relative w-full lg:w-2/3 rounded-2xl overflow-hidden shadow-lg ring-1 ring-orange-100 group">
          <Carousel
            ref={carouselRef}
            autoplay
            autoplaySpeed={4000}
            effect="fade"
            dots={{ className: 'custom-carousel-dots' }}
            className="rounded-2xl"
          >
            {bannerImages.map((img, idx) => (
              <div key={idx}>
                <div className="relative w-full h-70 sm:h-85 md:h-100">
                  <Image
                    src={img.src}
                    alt={img.alt}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 66vw"
                    priority={idx === 0}
                  />
                        {/* Warm gradient overlay */}
                        <div className="absolute inset-0 bg-linear-to-t from-orange-900/20 via-transparent to-transparent" />
                </div>
              </div>
            ))}
          </Carousel>
          {/* Custom Arrow Buttons */}
          <button
            onClick={() => carouselRef.current?.prev()}
                      className="absolute left-3 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-orange-50 rounded-full p-2 shadow-md opacity-0 group-hover:opacity-100 transition-all duration-300 z-10 cursor-pointer hover:scale-110"
          >
                      <ChevronLeft size={22} className="text-orange-700" />
          </button>
          <button
            onClick={() => carouselRef.current?.next()}
                      className="absolute right-3 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-orange-50 rounded-full p-2 shadow-md opacity-0 group-hover:opacity-100 transition-all duration-300 z-10 cursor-pointer hover:scale-110"
          >
                      <ChevronRight size={22} className="text-orange-700" />
          </button>
        </div>

        {/* Side Images */}
        <div className="hidden lg:flex flex-col gap-4 w-1/3">
          {sideImages.map((img, idx) => (
            <div
              key={idx}
                  className="relative flex-1 rounded-2xl overflow-hidden shadow-lg ring-1 ring-orange-100 hover:shadow-xl hover:ring-orange-200 transition-all duration-300 cursor-pointer group"
            >
              <Image
                src={img.src}
                alt={img.alt}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-500"
                sizes="33vw"
              />
                  <div className="absolute inset-0 bg-linear-to-t from-orange-900/30 to-transparent" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
