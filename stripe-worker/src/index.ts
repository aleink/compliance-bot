// ─── Minimal Stripe signature verifier ─────────────────────────────
async function verifyStripeSignature(
  payload: string,
  header: string,
  secret: string,
  toleranceSec = 300
): Promise<any> {
  const ts   = Number(/t=(\d+)/.exec(header)?.[1]);
  const sig  = /v1=([0-9a-f]+)/.exec(header)?.[1];
  if (!ts || !sig) throw new Error("bad header");
  if (Math.floor(Date.now() / 1000) - ts > toleranceSec) throw new Error("timeout");

  const data = `${ts}.${payload}`;
  const key  = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const digest = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(data));
  const hex    = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2,"0")).join("");

  if (hex !== sig) throw new Error("sig‑mismatch");
  return JSON.parse(payload);
}
// ───────────────────────────────────────────────────────────────────

export default {
  async fetch(req: Request, env: Record<string, string>) {
    if (req.method !== "POST") return new Response("ok");

    const rawBody = await req.text();
    const sigHdr  = req.headers.get("stripe-signature") ?? "";

    let event: any;
    try {
      event = await verifyStripeSignature(rawBody, sigHdr, env.STRIPE_SIGNING_SECRET);
    } catch (err) {
      return new Response("bad sig", { status: 400 });
    }

    if (event.type === "checkout.session.completed") {
      const email = event.data.object.customer_details.email;
      const site  = event.data.object.metadata?.site_url ?? "";

      const rsp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
        method: "POST",
        headers: {
          "Authorization": `token ${env.GITHUB_PAT}`,
          "Accept":        "application/vnd.github.everest-preview+json",
          "Content-Type":  "application/json"
        },
        body: JSON.stringify({
          event_type: "run_audit",
          client_payload: { email, site }
        })
      });

      console.log("GitHub dispatch response:", rsp.status);
    }

    return new Response("ok");
  }
};
