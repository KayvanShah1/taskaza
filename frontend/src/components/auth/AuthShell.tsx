"use client";

import Link from "next/link";
import { LogoIcon } from "@/components/logo";

export function AuthShell({
	title,
	subtitle,
	children,
	footer,
}: {
	title: string;
	subtitle?: string;
	children: React.ReactNode;
	footer?: React.ReactNode;
}) {
	return (
		<section className="flex min-h-screen bg-zinc-50 px-4 py-16 md:py-32 dark:bg-transparent">
			<div className="bg-muted m-auto h-fit w-full max-w-md overflow-hidden rounded-[calc(var(--radius)+.125rem)] border shadow-md shadow-zinc-950/5 dark:[--color-muted:var(--color-zinc-900)]">
				<div className="bg-card -m-px rounded-[calc(var(--radius)+.125rem)] border p-8 pb-6">
					<div className="text-center">
						<Link href="/" aria-label="go home" className="mx-auto block w-fit">
							<LogoIcon />
						</Link>
						<h1 className="mt-4 mb-1 text-xl font-semibold">{title}</h1>
						{subtitle ? <p className="text-sm">{subtitle}</p> : null}
					</div>
					<div className="mt-6">{children}</div>
				</div>
				{footer ? <div className="p-3">{footer}</div> : null}
			</div>
		</section>
	);
}
