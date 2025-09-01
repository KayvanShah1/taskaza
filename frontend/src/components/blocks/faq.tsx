"use client";

import { faqs } from "@/data/faqs";

export default function FAQ() {
	return (
		<section className="scroll-py-16 py-16 md:scroll-py-32 md:py-32" id="faqs">
			<div className="mx-auto max-w-5xl px-6">
				<div className="grid gap-y-12 px-2 lg:[grid-template-columns:1fr_auto]">
					<div className="text-center lg:text-left">
						<h2 className="mb-4 text-3xl font-semibold md:text-4xl">
							Frequently <br className="hidden lg:block" /> Asked <br className="hidden lg:block" />
							Questions
						</h2>
						<p>Quick answers about Taskaza’s AI, API, and dashboard.</p>
					</div>
					<div className="divide-y divide-dashed sm:mx-auto sm:max-w-lg lg:mx-0">
						{faqs.map((f, i) => (
							<div className={i === 0 ? "pb-6" : "py-6"} key={i}>
								<h3 className="text-base font-medium">{f.question}</h3>
								<p className="text-muted-foreground mt-4 text-base">{f.answer}</p>
							</div>
						))}
					</div>
				</div>
			</div>
		</section>
	);
}
