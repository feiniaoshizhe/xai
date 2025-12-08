import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { CopilotProvider } from "./providers";
import "@copilotkit/react-ui/styles.css";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Flight Chart Assistant",
  description: "机票价格查询与图表生成助手",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <CopilotProvider>
          {children}
        </CopilotProvider>
      </body>
    </html>
  );
}
