export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
export type Endpoint = Readonly<{ method: HttpMethod; path: string }>;

export const Backend = {
	Signup: { method: "POST", path: "/signup" } as const,
	Token: { method: "POST", path: "/token" } as const,
	UsersMe: { method: "GET", path: "/users/me" } as const,
	Tasks: { method: "GET", path: "/tasks" } as const,
	TaskGet: (id: string | number) => ({ method: "GET", path: `/tasks/${id}` }) as const,
	TaskCreate: { method: "POST", path: "/tasks" } as const,
	TaskUpdate: (id: string | number) => ({ method: "PUT", path: `/tasks/${id}` }) as const,
	TaskDelete: (id: string | number) => ({ method: "DELETE", path: `/tasks/${id}` }) as const,
} as const;

export const BFF = {
	Login: { method: "POST", path: "/api/auth/login" } as const,
	Logout: { method: "POST", path: "/api/auth/logout" } as const,
	Me: { method: "GET", path: "/api/auth/me" } as const,
	Proxy: (method: HttpMethod, p: string) => ({ method, path: `/api/${p.startsWith("/") ? p : "/" + p}` }) as const,
} as const;
