import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'Agent Chat',
  description: 'Chat with the thinking agent',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
