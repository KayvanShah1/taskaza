"use client";

import { Logo } from "@/components/logo";
import ThemeToggle from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import React from "react";
import { Separator } from "../ui/separator";

const menuItems = [
	{ name: "Features", href: "#features", external: false },
	{ name: "About", href: "#about", external: false },
	{ name: "API Docs", href: "https://taskaza.onrender.com/redoc", external: true },
];

export default function MarketingNavbar() {
	const [menuState, setMenuState] = React.useState(false);
	const [isScrolled, setIsScrolled] = React.useState(false);

	React.useEffect(() => {
		const onScroll = () => setIsScrolled(window.scrollY > 50);
		window.addEventListener("scroll", onScroll, { passive: true });
		return () => window.removeEventListener("scroll", onScroll);
	}, []);

	// close on ESC
	React.useEffect(() => {
		const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuState(false);
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, []);

	return (
		<header>
			<nav data-state={menuState ? "active" : undefined} className="fixed z-20 w-full px-2">
				<div
					className={cn(
						"mx-auto mt-2 px-6 transition-all duration-300 lg:px-12",
						isScrolled && "bg-background/50 max-w-4xl rounded-2xl border backdrop-blur-lg lg:px-5"
					)}
				>
					<div className="relative flex items-center justify-between py-3 lg:py-4">
						{/* Left: Logo */}
						<Link href="/" aria-label="home" className="flex items-center space-x-2">
							<Logo />
						</Link>

						{/* Center: Desktop nav */}
						<div className="hidden lg:block">
							<ul className="flex gap-8 text-sm">
								{menuItems.map((item, i) => (
									<li key={i}>
										<Link
											href={item.href}
											className="text-muted-foreground hover:text-accent-foreground block duration-150"
											{...(item.external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
										>
											<span>{item.name}</span>
										</Link>
									</li>
								))}
							</ul>
						</div>

						<div className="flex items-center gap-2">
							<Button asChild variant="outline" size="sm" className={cn(isScrolled && "lg:hidden")}>
								<Link href="#">
									<span>Login</span>
								</Link>
							</Button>
							<Button asChild size="sm" className={cn(isScrolled && "lg:hidden")}>
								<Link href="#">
									<span>Sign Up</span>
								</Link>
							</Button>
							<Button asChild size="sm" className={cn(isScrolled ? "hidden lg:inline-flex" : "hidden")}>
								<Link href="#">
									<span>Get Started</span>
								</Link>
							</Button>
							<Separator orientation="vertical" />
							<ThemeToggle />

							<button
								onClick={() => setMenuState((s) => !s)}
								aria-label={menuState ? "Close Menu" : "Open Menu"}
								aria-expanded={menuState}
								aria-controls="mobile-popover"
								className="relative -m-2.5 p-2.5 lg:hidden"
							>
								{menuState ? <X className="size-6" /> : <Menu className="size-6" />}
							</button>

							<div
								id="mobile-popover"
								role="menu"
								className={cn(
									"bg-background absolute top-full right-0 mt-2 hidden rounded-2xl border p-4 shadow-xl",
									"w-72 max-w-[85vw]", // <= control width here
									"animate-in fade-in-0 zoom-in-95 origin-top-right",
									menuState && "block lg:hidden"
								)}
							>
								<ul className="space-y-4 text-base">
									{menuItems.map((item, index) => (
										<li key={index}>
											<Link
												href={item.href}
												className="text-muted-foreground hover:text-accent-foreground block duration-150"
												{...(item.external
													? { target: "_blank", rel: "noopener noreferrer" }
													: {})}
												onClick={() => setMenuState(false)}
											>
												{item.name}
											</Link>
										</li>
									))}
								</ul>
							</div>
						</div>
					</div>
				</div>

				{menuState && (
					<button
						aria-hidden
						onClick={() => setMenuState(false)}
						className="fixed inset-0 z-[1] h-full w-full bg-transparent lg:hidden"
					/>
				)}
			</nav>
		</header>
	);
}
