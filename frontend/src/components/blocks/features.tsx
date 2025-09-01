import { features } from "@/data/features";

import { Cloud, Cpu, Fingerprint, Pencil, Settings2, Sparkles, Zap } from "lucide-react";

const iconFor = (title: string) => {
	switch (title) {
		case "AI assistance":
			return Sparkles;
		case "Fast dashboard":
			return Zap;
		case "Security first":
			return Fingerprint;
		case "REST API":
			return Settings2;
		case "Customizable tasks":
			return Pencil;
		case "Deployed live":
			return Cloud;
		default:
			return Cpu;
	}
};

export default function Features() {
	return (
		<section className="py-12 md:py-20" id="features">
			<div className="mx-auto max-w-5xl space-y-8 px-6 md:space-y-16">
				<div className="relative z-10 mx-auto max-w-xl space-y-6 text-center md:space-y-12">
					<h2 className="text-4xl font-medium text-balance lg:text-5xl">
						Built for fast, secure task management
					</h2>
					<p>
						Taskaza blends an AI agent, a clean dashboard, and secure APIs so you can create, organize, and
						manage your work with ease.
					</p>
				</div>

				<div className="relative mx-auto grid max-w-4xl divide-x divide-y rounded-2xl border *:p-12 sm:grid-cols-2 lg:grid-cols-3">
					{features.map((f) => {
						const Icon = iconFor(f.title);
						return (
							<div key={f.title} className="space-y-2">
								<div className="flex items-center gap-2">
									<Icon className="size-4" aria-hidden />
									<h3 className="text-sm font-medium">{f.title}</h3>
								</div>
								<p className="text-sm">{f.description}</p>
							</div>
						);
					})}
				</div>
			</div>
		</section>
	);
}
