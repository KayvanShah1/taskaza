"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Task = {
	id: number;
	title: string;
	description: string;
	status: "pending" | "completed";
	created_at: string;
};

export default function Dashboard() {
	const router = useRouter();
	const [username, setUsername] = useState<string | null>(null);
	const [tasks, setTasks] = useState<Task[]>([]);

	useEffect(() => {
		// user
		fetch("/api/me", { cache: "no-store" })
			.then((r) => (r.ok ? r.json() : Promise.reject()))
			.then((d) => setUsername(d.username))
			.catch(() => router.push("/"));

		// tasks
		fetch("/api/tasks", { cache: "no-store" })
			.then(async (res) => {
				const data = await res.json().catch(() => null);
				if (!res.ok) {
					console.error("Tasks error:", data);
					setTasks([]);
					return;
				}
				const arr = Array.isArray(data) ? data : (data?.items ?? data?.tasks ?? []);
				setTasks(arr);
			})
			.catch((e) => {
				console.error("Tasks fetch failed:", e);
				setTasks([]);
			});
	}, [router]);

	async function handleLogout() {
		await fetch("/api/logout", { method: "POST" });
		router.push("/");
	}

	return (
		<section className="space-y-6 p-6">
			<div className="flex items-center justify-between">
				<h1 className="text-3xl font-bold">Dashboard</h1>
				<Button onClick={handleLogout}>Logout</Button>
			</div>

			{username && (
				<p>
					Welcome, <span className="font-semibold">{username}</span> 👋
				</p>
			)}

			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
				{tasks.length > 0 ? (
					tasks.map((task) => (
						<Card key={task.id}>
							<CardHeader>
								<CardTitle>{task.title}</CardTitle>
							</CardHeader>
							<CardContent>
								<p className="text-muted-foreground text-sm">{task.description || "No description"}</p>
								<p className="mt-2 text-xs">
									Status:{" "}
									<span
										className={task.status === "completed" ? "text-green-600" : "text-yellow-600"}
									>
										{task.status}
									</span>
								</p>
								<p className="text-muted-foreground text-xs">
									Created: {new Date(task.created_at).toLocaleString()}
								</p>
							</CardContent>
						</Card>
					))
				) : (
					<p>No tasks found.</p>
				)}
			</div>
		</section>
	);
}
