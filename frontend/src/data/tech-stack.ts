// Simple Icons slug list: https://simpleicons.org
// Use `customSrc` when a logo isn't available or you want an alternate mark.
export type TechLogo = {
	name: string;
	slug?: string; // simpleicons slug (e.g., "react", "nextdotjs")
	colorHex?: string; // hex without '#', e.g. "808080" for gray
	customSrc?: string; // full URL to svg fallback
	width?: number; // optional per-item override
	height?: number; // optional per-item override
};

export const TECH_STACK: TechLogo[] = [
	{ name: "Next.js", slug: "nextdotjs" },
	{ name: "React", slug: "react" },
	{ name: "TypeScript", slug: "typescript" },
	{ name: "TailwindCSS", slug: "tailwindcss" },
	{ name: "shadcn/ui", slug: "shadcnui" },
	{ name: "Python", slug: "python" },
	{ name: "FastAPI", slug: "fastapi" },
	{ name: "Pydantic", slug: "pydantic" },
	{ name: "SQLAlchemy", slug: "sqlalchemy" },
	{ name: "PostgreSQL", slug: "postgresql" },
	{ name: "Pytest", slug: "pytest" },
	{ name: "Docker", slug: "docker" },
	{ name: "GitHub Actions", slug: "githubactions" },
	{ name: "Vercel", slug: "vercel" },
	{ name: "Render", slug: "render" },
];
