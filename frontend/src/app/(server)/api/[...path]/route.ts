import { NextRequest } from "next/server";
import { BACKEND_URL, API_KEY } from "@/lib/api/env";
import { assertCsrfForUnsafe } from "@/lib/api/csrf";
import { getAccess } from "@/lib/api/cookies";

export const runtime = "nodejs";

type Params = { path?: string[] };

function sanitizeUpstreamHeaders(src: Headers) {
	const h = new Headers();
	for (const [k, v] of src.entries()) {
		const key = k.toLowerCase();
		// strip hop-by-hop + encoding/length that cause ERR_CONTENT_DECODING_FAILED
		if (
			key === "content-encoding" ||
			key === "content-length" ||
			key === "transfer-encoding" ||
			key === "connection" ||
			key === "keep-alive" ||
			key === "proxy-authenticate" ||
			key === "proxy-authorization" ||
			key === "te" ||
			key === "trailer" ||
			key === "upgrade"
		)
			continue;
		h.set(k, v);
	}
	if (!h.has("content-type")) h.set("content-type", "application/json; charset=utf-8");
	// mark that proxy touched it (optional)
	h.set("x-proxied-by", "taskaza-bff");
	return h;
}

export async function ALL(req: NextRequest, ctx: { params: Promise<Params> }) {
	try {
		const { path = [] } = await ctx.params;

		// never proxy auth handlers
		if (path[0] === "auth") {
			return new Response(JSON.stringify({ error: "Not found" }), {
				status: 404,
				headers: { "content-type": "application/json" },
			});
		}

		const method = req.method.toUpperCase();
		assertCsrfForUnsafe(method, req.headers);

		const targetPath = `/${path.join("/")}${req.nextUrl.search}`;
		const target = `${BACKEND_URL}${targetPath}`;

		// ---------- build upstream request ----------
		const headers = new Headers();
		headers.set("accept", req.headers.get("accept") ?? "*/*");
		headers.set("accept-encoding", "identity"); // <- DON’T let upstream compress

		const ct = req.headers.get("content-type");
		if (ct) headers.set("content-type", ct);

		const token = await getAccess();
		if (token) headers.set("authorization", `Bearer ${token}`);

		if (!API_KEY) {
			return new Response(JSON.stringify({ error: "Missing API key env", hint: "TSKZ_HTTP_API_KEY" }), {
				status: 500,
				headers: { "content-type": "application/json" },
			});
		}
		headers.set("x-api-key", API_KEY);

		const body = method === "GET" || method === "HEAD" ? undefined : (req.body as ReadableStream | null);

		const upstream = await fetch(target, {
			method,
			headers,
			body: body ?? undefined,
			cache: "no-store",
			credentials: "omit",
			...(body ? { duplex: "half" as const } : {}),
		});

		// ---------- normalize response ----------
		const buf = await upstream.arrayBuffer(); // fully buffer so we control payload
		const outHeaders = sanitizeUpstreamHeaders(upstream.headers);

		return new Response(buf, { status: upstream.status, headers: outHeaders });
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
	} catch (err: any) {
		return new Response(JSON.stringify({ error: "Proxy error", message: err?.message ?? String(err) }), {
			status: 502,
			headers: { "content-type": "application/json" },
		});
	}
}

export const GET = ALL;
export const POST = ALL;
export const PUT = ALL;
export const PATCH = ALL;
export const DELETE = ALL;
