import type { Metadata } from "next";
import { Vazirmatn } from "next/font/google";
import "./globals.css";

const vazirmatn = Vazirmatn({ subsets: ["latin", "arabic"] });

export const metadata: Metadata = {
  title: "Faranic Real Estate",
  description: "AI Powered Real Estate Analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa">
      <body className={vazirmatn.className}>
        {children}
      </body>
    </html>
  );
}
