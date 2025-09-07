import { NextRequest } from "next/server";
import { serverFetch } from "@/lib/api/http";
import { setAccess, setCsrf } from "@/lib/api/cookies";
import { makeCsrf } from "@/lib/api/csrf";

type SignupBody = { username: string; password: string };

export async function POST(req: NextRequest) {
	const { username, password } = (await req.json()) as SignupBody;

	// 1) Create user on the backend
	const createRes = await serverFetch("/signup", {
		method: "POST",
		headers: { "content-type": "application/json" },
		body: JSON.stringify({ username, password }),
	});

	if (!createRes.ok) {
		// surface backend error body/status to client
		return new Response(await createRes.text(), { status: createRes.status });
	}

	// 2) Auto-login to set cookies (optional but nicer UX)
	const tokenRes = await serverFetch<{ access_token: string; token_type?: string; expires_in?: number }>("/token", {
		method: "POST",
		headers: { "content-type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({ username, password }),
	});

	if (!tokenRes.ok) {
		// User exists but login failed (unlikely). Return 201 so client can redirect to login.
		return new Response(null, { status: 201 });
	}

	const { access_token, expires_in } = await tokenRes.jsonTyped();
	setAccess(access_token, typeof expires_in === "number" ? expires_in : undefined);
	setCsrf(makeCsrf());

	return new Response(null, { status: 204 }); // fully signed-in
}
