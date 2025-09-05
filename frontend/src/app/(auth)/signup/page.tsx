"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { AuthShell } from "@/components/auth/AuthShell";
import { TextField } from "@/components/form/TextField";
import { PasswordField } from "@/components/form/PasswordField";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { useAuthForm } from "@/lib/auth/useAuthForm";
import { SignUpSchema, type SignUpValues } from "@/lib/auth/schemas";

export default function SignUpPage() {
	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
		setError,
	} = useAuthForm<SignUpValues>(SignUpSchema, {
		firstname: "",
		lastname: "",
		email: "",
		pwd: "",
		confirm: "",
	});

	const onSubmit = async (values: SignUpValues) => {
		try {
			const res = await fetch("/api/auth/register", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					first_name: values.firstname,
					last_name: values.lastname,
					email: values.email,
					password: values.pwd,
				}),
			});
			if (!res.ok) {
				const data = (await res.json().catch(() => ({}))) as { detail?: string };
				setError("email", { type: "server", message: data?.detail ?? "Unable to create account" });
				return;
			}
			window.location.href = "/login";
		} catch {
			setError("email", { type: "server", message: "Network error. Try again." });
		}
	};

	return (
		<AuthShell
			title="Create a Taskaza Account"
			subtitle="Welcome! Create an account to get started"
			footer={
				<p className="text-accent-foreground text-center text-sm">
					Have an account ?
					<Button asChild variant="link" className="px-2" type="button">
						<Link href="/login">Sign In</Link>
					</Button>
				</p>
			}
		>
			<form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
				<div className="grid grid-cols-2 gap-3">
					<TextField
						id="firstname"
						label="First name"
						autoComplete="given-name"
						register={register("firstname")}
						error={errors.firstname}
					/>
					<TextField
						id="lastname"
						label="Last name"
						autoComplete="family-name"
						register={register("lastname")}
						error={errors.lastname}
					/>
				</div>

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
					autoComplete="new-password"
					register={register("pwd")}
					error={errors.pwd}
					linkSlot={
						<Button asChild variant="link" size="sm" type="button">
							<Link href="#" className="text-sm">
								Password rules
							</Link>
						</Button>
					}
				/>

				<PasswordField
					id="confirm"
					label="Confirm password"
					autoComplete="new-password"
					register={register("confirm")}
					error={errors.confirm}
				/>

				<Button className="w-full" type="submit" disabled={isSubmitting}>
					{isSubmitting ? (
						<>
							<Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating account…
						</>
					) : (
						"Create Account"
					)}
				</Button>

				<OAuthButtons disabled={isSubmitting} />
			</form>

			<div slot="footer" />
		</AuthShell>
	);
}
