import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	/* config options here */
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
