import React from "react";

const Layout = ({ children }: Readonly<{ children: React.ReactNode }>) => {
	return (
		<div className="flex min-h-screen flex-col">
			<main className="flex-1">{children}</main>
		</div>
	);
};

export default Layout;
