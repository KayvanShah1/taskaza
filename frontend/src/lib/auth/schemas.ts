import { z } from "zod";

export const LoginSchema = z.object({
	email: z.string().min(1, "Email is required").email("Enter a valid email"),
	pwd: z.string().min(8, "Password must be at least 8 characters"),
});

export const SignUpSchema = z
	.object({
		firstname: z.string().min(1, "First name is required").max(50),
		lastname: z.string().min(1, "Last name is required").max(50),
		email: z.string().min(1, "Email is required").email("Enter a valid email"),
		pwd: z
			.string()
			.min(8, "Password must be at least 8 characters")
			.regex(/[A-Z]/, "Must include at least one uppercase letter")
			.regex(/[a-z]/, "Must include at least one lowercase letter")
			.regex(/[0-9]/, "Must include at least one number"),
		confirm: z.string().min(1, "Please confirm your password"),
	})
	.superRefine(({ pwd, confirm }, ctx) => {
		if (pwd !== confirm) {
			ctx.addIssue({ code: "custom", path: ["confirm"], message: "Passwords do not match" });
		}
	});

export type LoginValues = z.infer<typeof LoginSchema>;
export type SignUpValues = z.infer<typeof SignUpSchema>;
