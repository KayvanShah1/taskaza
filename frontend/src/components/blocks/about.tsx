import { motion } from "motion/react";

export function About() {
	return (
		<section
			id="about"
			className="container mx-auto px-4 py-24 text-center"
		>
			<motion.div
				initial={{ opacity: 0, y: 20 }}
				whileInView={{ opacity: 1, y: 0 }}
				viewport={{ once: true }}
				className="mx-auto max-w-3xl space-y-4"
			>
				<h2 className="text-3xl font-bold tracking-tight">
					About Taskaza
				</h2>
				<p className="text-muted-foreground">
					Taskaza is a lightweight task manager enhanced with AI to
					automate your workflow and keep you focused on what matters.
				</p>
			</motion.div>
		</section>
	);
}

export default About;
