import { BACKEND_URL, CSRF_HEADER, API_KEY } from "@/lib/api/env";
import { getAccess, getCsrf } from "@/lib/api/cookies";
import { ensureCsrf } from "@/lib/api/csrf";

export async function serverFetch<T = unknown>(path: string, init: RequestInit = {}) {
	const url = path.startsWith("http") ? path : `${BACKEND_URL}${path.startsWith("/") ? "" : "/"}${path}`;
	ensureCsrf();

	const method = (init.method ?? "GET").toUpperCase();
	const headers = new Headers(init.headers ?? {});
	const token = getAccess();

	if (token && !headers.has("authorization")) headers.set("authorization", `Bearer ${token}`);
	if (!headers.has("X-API-Key")) headers.set("X-API-Key", API_KEY);

	if (/^(POST|PUT|PATCH|DELETE)$/i.test(method) && !headers.has(CSRF_HEADER)) {
		const csrf = await getCsrf();
		if (csrf) headers.set(CSRF_HEADER, csrf);
	}

	const res = await fetch(url, { ...init, headers, credentials: "omit", cache: "no-store" });
	(res as Response & { jsonTyped?: () => Promise<T> }).jsonTyped = async () => (await res.json()) as T;
	return res as Response & { jsonTyped: () => Promise<T> };
}
