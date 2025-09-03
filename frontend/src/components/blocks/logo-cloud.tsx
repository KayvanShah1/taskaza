"use client";

import Image from "next/image";
import { ChevronRight } from "lucide-react";
import type { TechLogo } from "@/data/tech-stack";

type LogoCloudProps = {
	id?: string;
	title?: string;
	className?: string;
	items: TechLogo[];
	columns?: number; // default 6
	maxWidth?: string; // e.g., "max-w-5xl"
	iconHeightClass?: string; // tailwind height class, e.g., "h-12"
	grayscaleHex?: string; // e.g., "808080" forces single gray tone via Simple Icons
	blurOnHover?: boolean; // default true
};

function siUrl(slug: string, colorHex?: string) {
	// Simple Icons CDN format: https://cdn.simpleicons.org/{slug}/{hex?}
	return colorHex ? `https://cdn.simpleicons.org/${slug}/${colorHex}` : `https://cdn.simpleicons.org/${slug}`;
}

export function LogoCloud({
	id = "logo-cloud",
	title = "Built with Tech Stack",
	className = "",
	items,
	columns = 6,
	maxWidth = "max-w-5xl",
	iconHeightClass = "h-12",
	grayscaleHex = "808080", // force a unified gray shade; set to "" to keep brand colors
	blurOnHover = true,
}: LogoCloudProps) {
	return (
		<section className="bg-background pt-16 pb-16 md:pb-32" id={id}>
			<div className={`group relative m-auto ${maxWidth} px-6 ${className}`}>
				<div className="absolute inset-0 z-10 flex scale-95 items-center justify-center opacity-0 duration-500 group-hover:scale-100 group-hover:opacity-100">
					<div className="block text-sm duration-150 hover:opacity-75">
						<span>{title}</span>
						<ChevronRight className="ml-1 inline-block size-3" />
					</div>
				</div>

				<div
					className={[
						"mx-auto mt-12 grid max-w-3xl",
						"gap-x-12 gap-y-10 transition-all duration-500",
						blurOnHover ? "group-hover:opacity-50 group-hover:blur-xs" : "",
						"sm:gap-x-16 sm:gap-y-14",
					].join(" ")}
					style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
				>
					{items.map((item) => {
						const src = item.customSrc
							? item.customSrc
							: item.slug
								? siUrl(item.slug, grayscaleHex || item.colorHex)
								: "";

						return (
							<div className="flex" key={item.name}>
								<Image
									className={[
										"mx-auto w-auto",
										iconHeightClass,
										grayscaleHex ? "" : "grayscale",
									].join(" ")}
									src={src}
									alt={`${item.name} Logo`}
									width={item.width ?? 140}
									height={item.height ?? 48}
								/>
							</div>
						);
					})}
				</div>
			</div>
		</section>
	);
}
