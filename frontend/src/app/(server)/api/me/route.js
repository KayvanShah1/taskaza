// app/api/me/route.ts
import { NextResponse } from "next/server";
import { getAccess } from "@/lib/api/cookies";
import jwt from "jsonwebtoken";

// Normally this should come from process.env.JWT_SECRET
// Must match the secret you used in FastAPI when creating JWTs
const JWT_SECRET = process.env.JWT_SECRET || "secret";

export async function GET() {
	const token = await getAccess();
	if (!token) {
		return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
	}

	try {
		// Verify the token with the same secret FastAPI used
		const payload = jwt.verify(token, JWT_SECRET);

		return NextResponse.json({
			username: payload.sub, // FastAPI by default puts username in "sub"
		});
	} catch {
		return NextResponse.json({ error: "Invalid token" }, { status: 401 });
	}
}
