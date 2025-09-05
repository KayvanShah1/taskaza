"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { AuthShell } from "@/components/auth/AuthShell";
import { TextField } from "@/components/form/TextField";
import { PasswordField } from "@/components/form/PasswordField";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { useAuthForm } from "@/lib/auth/useAuthForm";
import { LoginSchema, type LoginValues } from "@/lib/auth/schemas";

export default function LoginPage() {
	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
		setError,
	} = useAuthForm<LoginValues>(LoginSchema, { email: "", pwd: "" });

	const onSubmit = async (values: LoginValues) => {
		try {
			const res = await fetch("/api/auth/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(values),
			});
			if (!res.ok) {
				const data = (await res.json().catch(() => ({}))) as { detail?: string };
				const message = data?.detail ?? "Invalid credentials";
				setError("pwd", { type: "server", message });
				return;
			}
			window.location.href = "/dashboard";
		} catch {
			setError("email", { type: "server", message: "Network error. Try again." });
		}
	};

	return (
		<AuthShell
			title="Sign In to Taskaza"
			subtitle="Welcome back! Sign in to continue"
			footer={
				<p className="text-accent-foreground text-center text-sm">
					Don&apos;t have an account ?
					<Button asChild variant="link" className="px-2" type="button">
						<Link href="/signup">Create account</Link>
					</Button>
				</p>
			}
		>
			<form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
				<TextField
					id="email"
					label="Email"
					type="email"
					autoComplete="email"
					register={register("email")}
					error={errors.email}
				/>

				<PasswordField
					id="pwd"
					label="Password"
					autoComplete="current-password"
					register={register("pwd")}
					error={errors.pwd}
					linkSlot={
						<Button asChild variant="link" size="sm" type="button">
							<Link href="#" className="text-sm">
								Forgot your Password ?
							</Link>
						</Button>
					}
				/>

				<Button className="w-full" type="submit" disabled={isSubmitting}>
					{isSubmitting ? (
						<>
							<Loader2 className="mr-2 h-4 w-4 animate-spin" /> Signing in…
						</>
					) : (
						"Sign In"
					)}
				</Button>

				<OAuthButtons disabled={isSubmitting} />
			</form>

			<div slot="footer" />
		</AuthShell>
	);
}
