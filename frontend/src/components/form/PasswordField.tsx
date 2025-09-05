"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { FieldError } from "react-hook-form";

export function PasswordField({
	id = "password",
	label = "Password",
	autoComplete = "current-password",
	linkSlot, // optional "Forgot?" link
	register,
	error,
}: {
	id?: string;
	label?: string;
	autoComplete?: string;
	linkSlot?: React.ReactNode;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	register: ReturnType<any>;
	error?: FieldError;
}) {
	const [show, setShow] = useState(false);
	return (
		<div className="space-y-0.5">
			<div className="flex items-center justify-between">
				<Label htmlFor={id} className="text-sm">
					{label}
				</Label>
				{linkSlot}
			</div>

			<div className="relative">
				<Input
					id={id}
					type={show ? "text" : "password"}
					autoComplete={autoComplete}
					className="pr-10"
					aria-invalid={!!error || undefined}
					aria-describedby={error ? `${id}-error` : undefined}
					{...register}
				/>
				<button
					type="button"
					onClick={() => setShow((s) => !s)}
					className="focus-visible:ring-ring absolute top-1/2 right-2 -translate-y-1/2 rounded p-1 transition outline-none hover:opacity-80 focus-visible:ring-2"
					aria-label={show ? "Hide password" : "Show password"}
				>
					{show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
				</button>
			</div>

			{error && (
				<p id={`${id}-error`} className="text-destructive text-xs">
					{error.message}
				</p>
			)}
		</div>
	);
}
