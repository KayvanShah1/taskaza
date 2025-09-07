import { cookies } from "next/headers";
import { ACCESS_COOKIE, ACCESS_TTL, CSRF_COOKIE, isProd } from "@/lib/api/env";

const base = { httpOnly: true as const, secure: isProd, sameSite: "lax" as const, path: "/" };

export async function setAccess(token: string, maxAge = ACCESS_TTL) {
	(await cookies()).set(ACCESS_COOKIE, token, { ...base, maxAge });
}
export async function getAccess() {
	return (await cookies()).get(ACCESS_COOKIE)?.value ?? null;
}
export async function clearAuth() {
	const jar = await cookies();
	jar.delete(ACCESS_COOKIE);
	jar.delete(CSRF_COOKIE);
}

export async function setCsrf(token: string) {
	(await cookies()).set(CSRF_COOKIE, token, {
		httpOnly: false,
		secure: isProd,
		sameSite: "lax",
		path: "/",
		maxAge: 60 * 60 * 24 * 7,
	});
}
export async function getCsrf() {
	return (await cookies()).get(CSRF_COOKIE)?.value ?? null;
}
