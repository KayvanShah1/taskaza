import { clearAuth } from "@/lib/api/cookies";
export async function POST() {
	clearAuth();
	return new Response(null, { status: 204 });
}
