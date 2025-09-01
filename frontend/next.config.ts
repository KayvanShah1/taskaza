import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	images: {
		dangerouslyAllowSVG: true,
		remotePatterns: [
			{
				protocol: "https",
				hostname: "*",
			},
			{
				protocol: "https",
				hostname: "html.tailus.io",
				pathname: "/blocks/customers/**",
			},
		],
	},
};

export default nextConfig;
