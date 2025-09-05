"use client";

import FAQ from "@/components/blocks/faq";
import Features from "@/components/blocks/features";
import Hero from "@/components/blocks/hero";
import { LogoCloud } from "@/components/blocks/logo-cloud";
import { TECH_STACK } from "@/data/tech-stack";

export default function Home() {
	return (
		<>
			<Hero />
			<LogoCloud
				items={TECH_STACK}
				columns={5}
				iconHeightClass="h-12"
				grayscaleHex="808080" // comment out to keep brand colors, or set another gray
			/>
			<Features />
			<FAQ />
		</>
	);
}
