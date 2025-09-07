import { createHmac, randomBytes, timingSafeEqual } from "crypto";
import { CSRF_HEADER, CSRF_SECRET } from "@/lib/api/env";
import { getCsrf, setCsrf } from "@/lib/api/cookies";

export function makeCsrf(): string {
	const value = randomBytes(24).toString("hex");
	const sig = createHmac("sha256", CSRF_SECRET).update(value).digest("hex");
	return `${value}.${sig}`;
}
export function validCsrf(token: string): boolean {
	const [value, sig] = token.split(".");
	if (!value || !sig) return false;
	const expected = createHmac("sha256", CSRF_SECRET).update(value).digest("hex");
	try {
		return timingSafeEqual(Buffer.from(sig, "hex"), Buffer.from(expected, "hex"));
	} catch {
		return false;
	}
}
export function ensureCsrf() {
	if (!getCsrf()) setCsrf(makeCsrf());
}

export async function assertCsrfForUnsafe(method: string, headers: Headers) {
	if (!/^(POST|PUT|PATCH|DELETE)$/i.test(method)) return;
	const header = headers.get(CSRF_HEADER);
	const cookie = getCsrf();
	if (!header || !cookie || header !== (await cookie))
		throw new Response(JSON.stringify({ error: "CSRF mismatch" }), { status: 403 });
	if (!validCsrf(header)) throw new Response(JSON.stringify({ error: "CSRF invalid" }), { status: 403 });
}
