import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SamaadSetu (संवादसेतु) – Universal Citizen Intake & Triage Engine",
  description: "Modeled on Uttar Pradesh's CM Helpline 1076 and Jansunwai across 75 districts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi" className="h-full bg-slate-950 text-slate-100">
      <body className="h-full antialiased font-sans flex flex-col">{children}</body>
    </html>
  );
}
