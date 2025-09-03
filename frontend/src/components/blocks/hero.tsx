"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { TextEffect } from "@/components/ui/text-effect";
import { AnimatedGroup } from "@/components/ui/animated-group";

const transitionVariants = {
	item: {
		hidden: {
			opacity: 0,
			filter: "blur(12px)",
			y: 12,
		},
		visible: {
			opacity: 1,
			filter: "blur(0px)",
			y: 0,
			transition: {
				type: "spring",
				bounce: 0.3,
				duration: 1.5,
			},
		},
	},
} as const;

export default function Hero() {
	return (
		<>
			<main className="overflow-hidden">
				<div aria-hidden className="absolute inset-0 isolate hidden opacity-65 contain-strict lg:block">
					<div className="absolute top-0 left-0 h-320 w-140 -translate-y-87.5 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsla(0,0%,85%,.08)_0,hsla(0,0%,55%,.02)_50%,hsla(0,0%,45%,0)_80%)]" />
					<div className="absolute top-0 left-0 h-320 w-60 [translate:5%_-50%] -rotate-45 rounded-full bg-[radial-gradient(50%_50%_at_50%_50%,hsla(0,0%,85%,.06)_0,hsla(0,0%,45%,.02)_80%,transparent_100%)]" />
					<div className="absolute top-0 left-0 h-320 w-60 -translate-y-87.5 -rotate-45 bg-[radial-gradient(50%_50%_at_50%_50%,hsla(0,0%,85%,.04)_0,hsla(0,0%,45%,.02)_80%,transparent_100%)]" />
				</div>

				<section>
					<div className="relative pt-24 md:pt-36">
						<AnimatedGroup
							variants={{
								container: {
									visible: {
										transition: {
											delayChildren: 1,
										},
									},
								},
								item: {
									hidden: { opacity: 0, y: 20 },
									visible: {
										opacity: 1,
										y: 0,
										transition: { type: "spring", bounce: 0.3, duration: 2 },
									},
								},
							}}
							className="absolute inset-0 -z-20"
						>
							<Image
								src="https://images.unsplash.com/photo-1526289034009-0240ddb68ce3"
								alt="background"
								className="absolute inset-x-0 top-56 -z-20 hidden lg:top-32 dark:block"
								width="3276"
								height="4095"
							/>
							{/* <Image
								src="https://images.unsplash.com/photo-1519120944692-1a8d8cfc107f"
								alt="background"
								className="absolute inset-x-0 top-56 -z-20 lg:top-32 dark:hidden"
								width="3276"
								height="4095"
							/> */}
						</AnimatedGroup>

						<div
							aria-hidden
							className="absolute inset-0 -z-10 size-full [background:radial-gradient(125%_125%_at_50%_100%,transparent_0%,var(--color-background)_75%)]"
						/>

						<div className="mx-auto max-w-7xl px-6">
							<div className="text-center sm:mx-auto lg:mt-0 lg:mr-auto">
								<AnimatedGroup variants={transitionVariants}>
									<Link
										href="#link"
										className="hover:bg-background dark:hover:border-t-border bg-muted group mx-auto flex w-fit items-center gap-2 rounded-full border p-1 pl-4 shadow-md shadow-zinc-950/5 transition-colors duration-300 dark:border-t-white/5 dark:shadow-zinc-950"
									>
										<span className="rounded-full bg-auto px-2">AskBar</span>
										<span className="text-foreground text-sm">
											Manage tasks with natural language
										</span>
										<span className="dark:border-background block h-4 w-0.5 border-l bg-white dark:bg-zinc-700" />
										<div className="bg-background group-hover:bg-muted size-6 overflow-hidden rounded-full duration-500">
											<div className="flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0">
												<span className="flex size-6">
													<ArrowRight className="m-auto size-3" />
												</span>
												<span className="flex size-6">
													<ArrowRight className="m-auto size-3" />
												</span>
											</div>
										</div>
									</Link>
								</AnimatedGroup>

								<h1 className="mx-auto mt-8 max-w-4xl text-6xl text-balance md:text-7xl lg:mt-16 xl:text-[5.25rem]">
									{/* <TextEffect
										as="span"
										preset="fade-in-blur"
										speedSegment={0.3}
										className="font-semibold text-amber-500"
									>
										Taskaza
									</TextEffect>{" "} */}
									<TextEffect as="span" preset="fade-in-blur" speedSegment={0.3}>
										Taskaza keeps you organized
									</TextEffect>
								</h1>

								<TextEffect
									per="line"
									preset="fade-in-blur"
									speedSegment={0.3}
									delay={0.5}
									as="p"
									className="mx-auto mt-8 max-w-2xl text-lg text-balance"
								>
									Blends secure APIs, AI assistance, and a clean dashboard to help you manage tasks
									effortlessly.
								</TextEffect>

								<AnimatedGroup
									variants={{
										container: {
											visible: {
												transition: { staggerChildren: 0.05, delayChildren: 0.75 },
											},
										},
										...transitionVariants,
									}}
									className="mt-12 flex flex-col items-center justify-center gap-2 md:flex-row"
								>
									<div
										key={1}
										className="bg-foreground/10 rounded-[calc(var(--radius-xl)+0.125rem)] border p-0.5"
									>
										<Button asChild size="lg" className="rounded-xl px-5 text-base">
											<Link href="#link">
												<span className="text-nowrap">Get Started</span>
											</Link>
										</Button>
									</div>
									<Button
										key={2}
										asChild
										size="lg"
										variant="ghost"
										className="h-10.5 rounded-xl px-5"
									>
										<Link
											href="https://taskaza.onrender.com/redoc"
											target="_blank"
											rel="noopener noreferrer"
										>
											<span className="text-nowrap">API Docs</span>
										</Link>
									</Button>
								</AnimatedGroup>
							</div>
						</div>

						<AnimatedGroup
							variants={{
								container: {
									visible: { transition: { staggerChildren: 0.05, delayChildren: 0.75 } },
								},
								...transitionVariants,
							}}
						>
							<div className="relative mt-8 -mr-56 overflow-hidden px-2 sm:mt-12 sm:mr-0 md:mt-20">
								<div
									aria-hidden
									className="to-background absolute inset-0 z-10 bg-linear-to-b from-transparent from-35%"
								/>
								<div className="ring-background bg-background relative mx-auto max-w-6xl overflow-hidden rounded-2xl border p-4 shadow-lg ring-1 inset-shadow-2xs shadow-zinc-950/15 dark:inset-shadow-white/20">
									<Image
										className="bg-background relative hidden aspect-15/8 rounded-2xl dark:block"
										src="https://images.unsplash.com/photo-1634078111133-a1e12d6131b6"
										alt="Team collaboration dashboard"
										width={2700}
										height={1440}
										priority
									/>

									<Image
										className="border-border/25 relative z-2 aspect-15/8 rounded-2xl border dark:hidden"
										src="https://images.unsplash.com/photo-1590402494587-44b71d7772f6"
										alt="Task management interface"
										width={2700}
										height={1440}
										priority
									/>
								</div>
							</div>
						</AnimatedGroup>
					</div>
				</section>
			</main>
		</>
	);
}
