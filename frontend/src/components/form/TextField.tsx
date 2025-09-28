"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { FieldError } from "react-hook-form";

export function TextField({
	id,
	label,
	type = "text",
	autoComplete,
	register,
	error,
	className,
}: {
	id: string;
	label: string;
	type?: React.ComponentProps<typeof Input>["type"];
	autoComplete?: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	register: ReturnType<any>;
	error?: FieldError;
	className?: string;
}) {
	return (
		<div className="space-y-2">
			<Label htmlFor={id} className="block text-sm">
				{label}
			</Label>
			<Input
				id={id}
				type={type}
				autoComplete={autoComplete}
				aria-invalid={!!error || undefined}
				aria-describedby={error ? `${id}-error` : undefined}
				className={className}
				{...register}
			/>
			{error && (
				<p id={`${id}-error`} className="text-destructive text-xs">
					{error.message}
				</p>
			)}
		</div>
	);
}
