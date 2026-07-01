import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/layout/Sidebar'
import { QueryProvider } from '@/components/layout/QueryProvider'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'SDAS — Singapore Dividend Accumulation Screener',
  description: 'Screen SGX dividend stocks daily. Build towards SGD 5,000/month passive income.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#0B1929] text-white min-h-screen flex">
        <QueryProvider>
          <Sidebar />
          <main className="flex-1 overflow-auto">
            {children}
          </main>
          <Toaster
            position="top-right"
            toastOptions={{
              style: { background: '#132337', color: '#fff', border: '1px solid #C9A84C33' },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  )
}
