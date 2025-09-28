"use client";

import { DefaultValues, FieldValues, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useAuthForm<TValues extends FieldValues>(schema: any, defaults: Partial<TValues>) {
	return useForm<TValues>({
		resolver: zodResolver(schema),
		defaultValues: defaults as DefaultValues<TValues>,
		mode: "onSubmit",
		reValidateMode: "onChange",
	});
}
