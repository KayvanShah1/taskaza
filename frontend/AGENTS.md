# agents.md — Frontend Agent Integration Guide

This doc shows how to wire an **AI Agent + AskBar** into a modern **Next.js (App Router)** frontend using **TypeScript, shadcn/ui, Tailwind CSS, Framer Motion (motion), Origin UI, Tailark**. It covers folder layout, routing groups, component patterns, state/data fetching, and production-grade practices.

---

## 1) Project layout

```
src/
  app/
    (root)/
      page.tsx                 # Landing (hero, features, logo-cloud, CTA)
      layout.tsx               # Root marketing chrome (Navbar/Footer)
    dashboard/
      layout.tsx               # Dashboard shell (Sidebar + dashboard Navbar)
      page.tsx                 # /dashboard -> redirects to /dashboard/home
      home/page.tsx
      tasks/page.tsx
      agent/page.tsx           # AskBar + chat thread UI
      settings/page.tsx
      @modals/(..)
    api/                       # (optional) edge routes for proxies if needed
  components/
    agent/
      ask-bar.tsx
      chat-thread.tsx
      message-bubble.tsx
      tool-calls.tsx
      thinking-indicator.tsx
    ui/                        # shadcn components + wrappers (Button, Input, ...)
    layout/
      dashboard-sidebar.tsx
      dashboard-topnav.tsx
      marketing-navbar.tsx
      marketing-footer.tsx
    blocks/                    # Hero, Features, LogoCloud, CTA (composable blocks)
  lib/
    agent-client.ts            # Agent SDK wrapper (fetch + SSE)
    auth.ts                    # client helpers (tokens/headers)
    config.ts                  # env + runtime config
    utils.ts                   # clsx, formatters, etc.
    analytics.ts               # posthog/ga wrappers
    store/                     # zustand or jotai atoms (lightweight)
  data/
    features.ts                # static marketing data
    logos.ts
  styles/
    globals.css
  types/
    agent.ts                   # Agent request/response types
    task.ts
```

**Routing groups**

* `/app/(root)` → marketing (no auth)
* `/app/(dashboard)` → protected app (auth gate, per-user experience)
* Dashboard nav: **Home**, **Tasks**, **Agent**, **Settings**

---

## 2) Tech choices & conventions

* **Next.js App Router** (server components by default, client components only where needed).
* **UI**: shadcn/ui (primary), Origin UI & Tailark as pattern libraries for blocks.
* **Styling**: Tailwind; prefer `class-variance-authority` (`cva`) for variants.
* **Motion**: Framer Motion for micro-interactions (hover, in-view, enter/exit).
* **State**: lightweight (Zustand/Jotai) only for UI state & optimistic chat; avoid global when SSR/SC is enough.
* **Data fetching**: `fetch` with **server actions** or **Route Handlers**; use **SSE** for streaming agent replies.
* **Accessibility**: use shadcn semantics, ARIA roles, focus traps for dialogs, reduced-motion support.
* **Performance**: image optimization, RSC for heavy read paths, lazy client islands, route-level loading/suspense.
* **Security**: http-only cookies for auth, CSRF safe actions, no secrets in client bundles.

---

## 3) Environment & config

`src/lib/config.ts`

```ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL!,      // e.g. https://api.taskaza.app
  askEndpoint:  process.env.NEXT_PUBLIC_AGENT_ASK_URL!,   // e.g. /api/agent/ask (proxy) or direct
  sse:          { heartbeatMs: 15_000 },
} as const;
```

> Keep server secrets server-side only; expose just `NEXT_PUBLIC_*` when necessary. Prefer **/app/api** proxies to avoid CORS & hide headers.

---

## 4) Auth (client helpers)

`src/lib/auth.ts`

```ts
export function authHeaders() {
  const jwt = typeof window !== "undefined" ? localStorage.getItem("tskz.jwt") : null;
  const apiKey = process.env.NEXT_PUBLIC_TSKZ_HTTP_API_KEY; // public if required by backend design
  const headers: Record<string,string> = { "Content-Type": "application/json" };
  if (jwt) headers.Authorization = `Bearer ${jwt}`;
  if (apiKey) headers["X-API-Key"] = apiKey;
  return headers;
}
```

> If you can, **prefer http-only cookies** set by a Next Route Handler after login; then you won’t touch `localStorage` at all.

---

## 5) Agent SDK wrapper

`src/lib/agent-client.ts`

```ts
import { config } from "./config";
import { authHeaders } from "./auth";
import type { AgentMessage, AgentToolCall } from "@/types/agent";

export type AskPayload = {
  threadId?: string;
  message: string;
  context?: Record<string, unknown>; // user/task context
};

export type AskToken =
  | { type: "message_delta"; id: string; text: string }
  | { type: "message_done"; id: string }
  | { type: "tool_call"; tool: AgentToolCall }
  | { type: "error"; error: string };

export async function* askAgentSSE(payload: AskPayload): AsyncGenerator<AskToken> {
  const res = await fetch(config.askEndpoint, {
    method: "POST",
    headers: { ...authHeaders(), Accept: "text/event-stream" },
    body: JSON.stringify(payload),
  });
  if (!res.ok || !res.body) throw new Error(`Agent request failed: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    for (const line of buffer.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      if (!json) continue;
      yield JSON.parse(json) as AskToken;
    }
    buffer = "";
  }
}
```

> The proxy at `/app/api/agent/ask` should translate upstream streaming (OpenRouter/MCP/etc.) into SSE `data:` frames with the above token types.

---

## 6) AskBar (client component)

`src/components/agent/ask-bar.tsx`

```tsx
"use client";
import { useState, useRef } from "react";
import { Button, Input } from "@/components/ui"; // shadcn re-exports
import { askAgentSSE } from "@/lib/agent-client";

export function AskBar({ threadId }: { threadId?: string }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    abortRef.current = new AbortController();

    // emit user message to local store (optimistic)...
    // append to chat thread UI in parent

    try {
      for await (const token of askAgentSSE({ threadId, message: text })) {
        // route token to chat-thread via callback/store
        // message_delta -> append text
        // message_done -> finalize bubble
        // tool_call     -> show tool event (create task, etc.)
      }
    } finally {
      setLoading(false);
      setText("");
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex gap-2 w-full">
      <Input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask your agent to create/update tasks…"
        aria-label="Ask the task agent"
      />
      <Button type="submit" disabled={loading}>Ask</Button>
    </form>
  );
}
```

---

## 7) Agent page (dynamic route)

`src/app/(dashboard)/agent/page.tsx`

```tsx
import { Suspense } from "react";
import { AskBar } from "@/components/agent/ask-bar";
import ChatThread from "@/components/agent/chat-thread";

export default function AgentPage() {
  // Optional: read threadId from searchParams
  return (
    <div className="flex h-full flex-col gap-4">
      <Suspense fallback={<div className="p-4">Loading conversation…</div>}>
        <ChatThread />
      </Suspense>
      <AskBar />
    </div>
  );
}
```

---

## 8) Dashboard shell (sidebar + navbar)

`src/components/layout/dashboard-sidebar.tsx`

```tsx
import Link from "next/link";
import { Home, ListTodo, MessageSquare, Settings } from "lucide-react";

const items = [
  { href: "/dashboard/home", icon: Home, label: "Home" },
  { href: "/dashboard/tasks", icon: ListTodo, label: "Tasks" },
  { href: "/dashboard/agent", icon: MessageSquare, label: "Agent" },
  { href: "/dashboard/settings", icon: Settings, label: "Settings" },
];

export default function DashboardSidebar() {
  return (
    <aside className="w-60 border-r bg-card">
      <nav className="p-3 space-y-1">
        {items.map(({ href, icon: Icon, label }) => (
          <Link key={href} href={href} className="flex items-center gap-2 rounded px-2 py-2 hover:bg-accent">
            <Icon className="size-4" /> <span>{label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

`src/app/(dashboard)/layout.tsx`

```tsx
import DashboardSidebar from "@/components/layout/dashboard-sidebar";
import DashboardTopnav from "@/components/layout/dashboard-topnav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid h-dvh grid-cols-[15rem_1fr]">
      <DashboardSidebar />
      <div className="flex flex-col">
        <DashboardTopnav />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
```

---

## 9) Landing page blocks (marketing)

* **Hero** (USP + screenshot + primary CTA → `/dashboard/agent`)
* **Logo cloud** (social proof)
* **Features** (cards: “Natural-language tasks”, “Secure auth”, “Live preview”)
* **CTA** (signup or open demo thread)

Use Origin UI/Tailark blocks as references; wrap them into `components/blocks/*` for reusability.

---

## 10) Tool calls (UI & plumbing)

When the agent executes actions (e.g., **create task**), stream a `tool_call` token with minimal payload. The UI should:

1. Render a small **tool call chip** (e.g., “Creating task …”).
2. Optimistically add/update the Task list.
3. Reconcile with server on `message_done`.

`src/components/agent/tool-calls.tsx`

```tsx
export function ToolCallChip({ name, status }: { name: string; status: "running" | "ok" | "error" }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border px-2 py-1 text-xs">
      <span className="size-2 rounded-full bg-muted-foreground" />
      {name} — {status}
    </span>
  );
}
```

---

## 11) Accessibility & motion

* Respect `prefers-reduced-motion`; gate Motion transitions:

```tsx
import { useReducedMotion, motion } from "framer-motion";
const shouldReduce = useReducedMotion();
<motion.div initial={shouldReduce ? false : { opacity: 0, y: 8 }} animate={shouldReduce ? {} : { opacity: 1, y: 0 }} />
```

* Use focus outlines, `aria-live="polite"` for streaming text, and keyboard navigation in chat.

---

## 12) Production checklist

* **Type safety**: All components typed; shared `types/agent.ts`.
* **ESLint/Prettier**: strict; unused imports error; import sorting.
* **Tailwind**: colocation via `className`; avoid deep CSS unless necessary.
* **shadcn**: don’t edit generated primitives; wrap with `components/ui/*`.
* **Error boundaries**: `error.tsx` & `not-found.tsx` per route segment.
* **Loading states**: `loading.tsx` with skeletons for dashboard pages.
* **Analytics**: basic page + event tracking (AskBar submit, tool success/fail).
* **Auth gate**: server `redirect()` to `/signin` for dashboard segment.
* **Cache strategy**: `fetch` with `cache: "no-store"` for chat; ISR for marketing.
* **SSE keepalive**: heartbeat server -> client every 15s.
* **CSP**: strict; allow `connect-src` to API and SSE endpoints.
* **SEO**: `metadata` export in root routes.
* **i18n (optional)**: `next-intl` if needed later.

---

## 13) Minimal API proxy (optional but recommended)

`src/app/api/agent/ask/route.ts`

```ts
import { NextRequest } from "next/server";
import { config } from "@/lib/config";

export const runtime = "edge";

export async function POST(req: NextRequest) {
  const body = await req.text(); // forward raw body
  const upstream = await fetch(`${config.apiBaseUrl}/ask-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // attach server-side secrets or cookies here
      "X-API-Key": process.env.TSKZ_HTTP_API_KEY!,
      Authorization: req.headers.get("authorization") ?? "",
      Accept: "text/event-stream",
    },
    body,
  });

  if (!upstream.ok || !upstream.body) {
    return new Response("Upstream error", { status: 502 });
  }

  // Stream-through SSE
  return new Response(upstream.body, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
```

---

## 14) Testing & quality

* **Unit**: component logic & utils with Vitest + React Testing Library.
* **E2E**: Playwright (happy path: login → /dashboard/agent → ask → tool call).
* **Lint**: `pnpm lint` in CI; **typecheck** `tsc --noEmit`.
* **Preview deploys**: Vercel/Netlify with env protection.

---

## 15) How to add a new agent feature

1. **Define message schema** in `types/agent.ts`.
2. **Update SDK** in `lib/agent-client.ts` to recognize new `tool_call` type.
3. **Render UI** for the tool in `components/agent/tool-calls.tsx`.
4. **Wire optimistic updates** (e.g., `useTaskStore()`).
5. **Add tests** for token pipeline & rendering.
6. **Document** prompt/usage in this file (append below).

---

## 16) Quick start commands

```bash
# Dev
pnpm i
pnpm dev

# Lint & typecheck
pnpm lint
pnpm typecheck

# Test
pnpm test
pnpm e2e
```

---

## 17) Agent message types (example)

`src/types/agent.ts`

```ts
export type Role = "user" | "assistant" | "tool";
export interface ChatMessage {
  id: string;
  role: Role;
  text?: string;
  createdAt: string;
  toolCallId?: string;
}

export interface AgentToolCall {
  name: "create_task" | "update_task" | "list_tasks";
  args: Record<string, unknown>;
  status?: "running" | "ok" | "error";
}
```

---

## 18) UX rules of thumb

* The **AskBar is the primary action**—always visible on `/dashboard/agent`.
* Keep **latency perceivable** (typing indicator, progressive streaming).
* **Undo/confirm** for destructive tool calls (“Delete task?”).
* **Empty states** everywhere (tasks, chat, settings).
* Respect **reduced motion** & **keyboard-first** usage.

---

**That’s it.** With this structure and the sample code, you can ship a professional, production-grade **AskBar + Agent** experience inside your Next.js App Router app, with clean UI primitives (shadcn), performance-friendly RSC, and robust streaming via SSE.
