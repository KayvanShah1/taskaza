import { NextRequest } from "next/server";
import { serverFetch } from "@/lib/api/http";
import { setAccess, setCsrf } from "@/lib/api/cookies";
import { makeCsrf } from "@/lib/api/csrf";

type LoginBody = { username: string; password: string };

export async function POST(req: NextRequest) {
	const { username, password } = (await req.json()) as LoginBody;

	// FastAPI uses form for /token (OAuth2 password)
	const body = new URLSearchParams({ username, password });

	const res = await serverFetch<{ access_token: string; token_type?: string; expires_in?: number }>("/token", {
		method: "POST",
		body,
		headers: { "content-type": "application/x-www-form-urlencoded" },
	});

	if (!res.ok) return new Response(await res.text(), { status: res.status });

	const { access_token, expires_in } = await res.jsonTyped();
	setAccess(access_token, typeof expires_in === "number" ? expires_in : undefined);
	setCsrf(makeCsrf());

	return new Response(null, { status: 204 });
}
