// app/(auth)/layout.tsx
import React from "react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
	// keep it minimal; you can add a tiny header with just a logo if you want
	return <main className="min-h-screen">{children}</main>;
}
