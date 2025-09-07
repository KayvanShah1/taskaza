export const isProd = process.env.NODE_ENV === "production";
export const BACKEND_URL = process.env.TSKZ_BACKEND_URL ?? "https://taskaza.onrender.com";

export const ACCESS_COOKIE = process.env.TSKZ_ACCESS_COOKIE ?? "tskz_at";
export const CSRF_COOKIE = process.env.TSKZ_CSRF_COOKIE ?? "tskz_csrf";
export const ACCESS_TTL = Number(process.env.TSKZ_ACCESS_TTL ?? 900);

export const CSRF_HEADER = process.env.TSKZ_CSRF_HEADER ?? "x-csrf-token";
export const API_KEY = process.env.TSKZ_API_KEY ?? "123456"; // match FastAPI requirement
export const CSRF_SECRET = process.env.TSKZ_CSRF_SECRET ?? "";

if (!BACKEND_URL) throw new Error("TSKZ_BACKEND_URL missing");
if (!CSRF_SECRET) throw new Error("BFF_CSRF_SECRET missing");
