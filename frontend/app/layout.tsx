import type { Metadata } from 'next'
import { AuthProvider } from './context/AuthContext'
import './globals.css'

export const metadata: Metadata = {
  title: 'Data Protection Simulator',
  description: 'Learn cybersecurity through interactive attack scenarios',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
