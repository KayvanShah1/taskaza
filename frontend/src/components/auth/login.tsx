"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";

import { LogoIcon } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";

const LoginSchema = z.object({
	email: z.string().min(1, "Email is required").email("Enter a valid email"),
	pwd: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginValues = z.infer<typeof LoginSchema>;

export default function LoginForm() {
	const [showPwd, setShowPwd] = useState(false);
	const [serverError, setServerError] = useState<string | null>(null);

	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
		setError,
	} = useForm<LoginValues>({
		resolver: zodResolver(LoginSchema),
		defaultValues: { email: "", pwd: "" },
		mode: "onSubmit",
		reValidateMode: "onChange",
	});

	const onSubmit = async (values: LoginValues) => {
		setServerError(null);
		try {
			// Replace with your real endpoint (BFF/Next route or FastAPI)
			// Example using a Next.js route: /api/auth/login
			const res = await fetch("/api/auth/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(values),
			});

			if (!res.ok) {
				const data = (await res.json().catch(() => ({}))) as { detail?: string };
				const message = data?.detail ?? "Invalid credentials";
				// put the error on the password field by default
				setError("pwd", { type: "server", message });
				setServerError(message);
				return;
			}

			// success: redirect or refresh
			// e.g., router.push("/dashboard") or window.location.href = "/"
			window.location.href = "/dashboard";
		} catch {
			setServerError("Something went wrong. Please try again.");
		}
	};

	return (
		<section className="flex min-h-screen bg-zinc-50 px-4 py-16 md:py-32 dark:bg-transparent">
			<form
				onSubmit={handleSubmit(onSubmit)}
				className="bg-muted m-auto h-fit w-full max-w-md overflow-hidden rounded-[calc(var(--radius)+.125rem)] border shadow-md shadow-zinc-950/5 dark:[--color-muted:var(--color-zinc-900)]"
				noValidate
			>
				<div className="bg-card -m-px rounded-[calc(var(--radius)+.125rem)] border p-8 pb-6">
					<div className="text-center">
						<Link href="/" aria-label="go home" className="mx-auto block w-fit">
							<LogoIcon />
						</Link>
						<h1 className="mt-4 mb-1 text-xl font-semibold">Sign In to Taskaza</h1>
						<p className="text-sm">Welcome back! Sign in to continue</p>
					</div>

					<div className="mt-6 space-y-6">
						{/* Email */}
						<div className="space-y-2">
							<Label htmlFor="email" className="block text-sm">
								Email
							</Label>
							<Input
								id="email"
								type="email"
								autoComplete="email"
								aria-invalid={!!errors.email || undefined}
								aria-describedby={errors.email ? "email-error" : undefined}
								{...register("email")}
							/>
							{errors.email && (
								<p id="email-error" className="text-destructive text-xs">
									{errors.email.message}
								</p>
							)}
						</div>

						{/* Password with eye toggle */}
						<div className="space-y-0.5">
							<div className="flex items-center justify-between">
								<Label htmlFor="pwd" className="text-sm">
									Password
								</Label>
								<Button asChild variant="link" size="sm" type="button">
									<Link href="#" className="link intent-info variant-ghost text-sm">
										Forgot your Password ?
									</Link>
								</Button>
							</div>

							<div className="relative">
								<Input
									id="pwd"
									type={showPwd ? "text" : "password"}
									autoComplete="current-password"
									className="input sz-md variant-mixed pr-10"
									aria-invalid={!!errors.pwd || undefined}
									aria-describedby={errors.pwd ? "pwd-error" : undefined}
									{...register("pwd")}
								/>
								<button
									type="button"
									onClick={() => setShowPwd((s) => !s)}
									className="focus-visible:ring-ring absolute top-1/2 right-2 -translate-y-1/2 rounded p-1 ring-0 transition outline-none hover:opacity-80 focus-visible:ring-2"
									aria-label={showPwd ? "Hide password" : "Show password"}
								>
									{showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
								</button>
							</div>
							{errors.pwd && (
								<p id="pwd-error" className="text-destructive text-xs">
									{errors.pwd.message}
								</p>
							)}
						</div>

						{/* Server error (form-level) */}
						{serverError && (
							<div className="border-destructive/30 bg-destructive/5 text-destructive rounded-md border p-3 text-xs">
								{serverError}
							</div>
						)}

						<Button className="w-full" type="submit" disabled={isSubmitting}>
							{isSubmitting ? (
								<>
									<Loader2 className="mr-2 h-4 w-4 animate-spin" />
									Signing in…
								</>
							) : (
								"Sign In"
							)}
						</Button>
					</div>

					<div className="my-6 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
						<hr className="border-dashed" />
						<span className="text-muted-foreground text-xs">Or continue With</span>
						<hr className="border-dashed" />
					</div>

					<div className="grid grid-cols-2 gap-3">
						<Button type="button" variant="outline" disabled={isSubmitting}>
							{/* Google icon */}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="0.98em"
								height="1em"
								viewBox="0 0 256 262"
								aria-hidden="true"
							>
								<path
									fill="#4285f4"
									d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622l38.755 30.023l2.685.268c24.659-22.774 38.875-56.282 38.875-96.027"
								></path>
								<path
									fill="#34a853"
									d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055c-34.523 0-63.824-22.773-74.269-54.25l-1.531.13l-40.298 31.187l-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1"
								></path>
								<path
									fill="#fbbc05"
									d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82c0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602z"
								></path>
								<path
									fill="#eb4335"
									d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0C79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251"
								></path>
							</svg>
							<span>Google</span>
						</Button>
						<Button type="button" variant="outline" disabled={isSubmitting}>
							{/* Microsoft icon */}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="1em"
								height="1em"
								viewBox="0 0 256 256"
								aria-hidden="true"
							>
								<path fill="#f1511b" d="M121.666 121.666H0V0h121.666z"></path>
								<path fill="#80cc28" d="M256 121.666H134.335V0H256z"></path>
								<path fill="#00adef" d="M121.663 256.002H0V134.336h121.663z"></path>
								<path fill="#fbbc09" d="M256 256.002H134.335V134.336H256z"></path>
							</svg>
							<span>Microsoft</span>
						</Button>
					</div>
				</div>

				<div className="p-3">
					<p className="text-accent-foreground text-center text-sm">
						Don&apos;t have an account ?
						<Button asChild variant="link" className="px-2" type="button">
							<Link href="/signup">Create account</Link>
						</Button>
					</p>
				</div>
			</form>
		</section>
	);
}
