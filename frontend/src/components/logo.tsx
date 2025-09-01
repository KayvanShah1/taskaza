import { cn } from "@/lib/utils";

export const Logo = ({
	className,
	uniColor,
}: {
	className?: string;
	uniColor?: boolean;
}) => (
	<svg
		viewBox="0 0 120 24"
		xmlns="http://www.w3.org/2000/svg"
		className={cn("h-5 w-auto", className)}
	>
		<defs>
			<linearGradient
				id="logo-gradient"
				x1="0"
				y1="0"
				x2="0"
				y2="24"
				gradientUnits="userSpaceOnUse"
			>
				<stop stopColor="#9B99FE" />
				<stop offset="1" stopColor="#2BC8B7" />
			</linearGradient>
		</defs>
		<rect
			width="24"
			height="24"
			rx="5"
			fill={uniColor ? "currentColor" : "url(#logo-gradient)"}
		/>
		<path d="M7 6h10v4h-3v12h-4V10H7V6z" fill="white" />
		<text
			x="32"
			y="19"
			fontSize="20"
			fontWeight="bold"
			fill={uniColor ? "currentColor" : "url(#logo-gradient)"}
		>
			Taskaza
		</text>
	</svg>
);

export const LogoIcon = ({
	className,
	uniColor,
}: {
	className?: string;
	uniColor?: boolean;
}) => (
	<svg
		viewBox="0 0 24 24"
		xmlns="http://www.w3.org/2000/svg"
		className={cn("h-6 w-6", className)}
	>
		<defs>
			<linearGradient
				id="logo-gradient"
				x1="0"
				y1="0"
				x2="0"
				y2="24"
				gradientUnits="userSpaceOnUse"
			>
				<stop stopColor="#9B99FE" />
				<stop offset="1" stopColor="#2BC8B7" />
			</linearGradient>
		</defs>
		<rect
			width="24"
			height="24"
			rx="5"
			fill={uniColor ? "currentColor" : "url(#logo-gradient)"}
		/>
		<path d="M7 6h10v4h-3v12h-4V10H7V6z" fill="white" />
	</svg>
);

export const LogoStroke = ({ className }: { className?: string }) => (
	<svg
		viewBox="0 0 24 24"
		xmlns="http://www.w3.org/2000/svg"
		className={cn("h-6 w-6", className)}
	>
		<rect width="24" height="24" rx="5" fill="none" stroke="currentColor" />
		<path
			d="M7 6h10v4h-3v12h-4V10H7V6z"
			fill="none"
			stroke="currentColor"
		/>
	</svg>
);
