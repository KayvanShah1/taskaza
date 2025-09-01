import MarketingNavbar from "@/components/layout/landing-page/marketing-navbar";
import MarketingFooter from "@/components/layout/landing-page/marketing-footer";
import React from "react";

const Layout = ({ children }: Readonly<{ children: React.ReactNode }>) => {
	return (
		<div className="flex min-h-screen flex-col">
			<MarketingNavbar />
			<main className="flex-1">{children}</main>
			<MarketingFooter />
		</div>
	);
};

export default Layout;
