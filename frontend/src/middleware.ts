// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { CSRF_HEADER } from "@/lib/api/env";

// run only for /api/* but skip /api/auth/*
export function middleware(req: NextRequest) {
	const p = req.nextUrl.pathname;

	if (!p.startsWith("/api/")) return NextResponse.next();
	if (p.startsWith("/api/auth/")) return NextResponse.next(); // allow login/signup w/o CSRF
	if (!/^(POST|PUT|PATCH|DELETE)$/i.test(req.method)) return NextResponse.next();

	const header = req.headers.get(CSRF_HEADER);
	const cookie = req.cookies.get(process.env.TSKZ_CSRF_COOKIE ?? "tskz_csrf")?.value;

	if (!header || !cookie || header !== cookie) {
		return new NextResponse(JSON.stringify({ error: "CSRF validation failed" }), {
			status: 403,
			headers: { "content-type": "application/json" },
		});
	}
	return NextResponse.next();
}

// only apply to /api/*
export const config = { matcher: ["/api/:path*"] };
