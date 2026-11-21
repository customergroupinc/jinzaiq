// JINZAiQ external schedule trigger.
// Deploy to a Cloudflare Worker with a secret named GITHUB_TOKEN.
// The Worker does not provide an HTTP-based dispatch endpoint.
const DISPATCH_URL =
  "https://api.github.com/repos/customergroupinc/jinzaiq/actions/workflows/update-news.yml/dispatches";
const ALLOWED_CRONS = new Set(["7 3,9,21 * * *"]);

export default {
  async fetch() {
    return new Response("Not found", { status: 404 });
  },
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(dispatch(controller, env));
  },
};

async function dispatch(controller, env) {
  if (!ALLOWED_CRONS.has(controller.cron)) {
    throw new Error("Unexpected cron: " + controller.cron);
  }
  if (!env.GITHUB_TOKEN) {
    throw new Error("Cloudflare secret GITHUB_TOKEN is missing");
  }
  let lastStatus = "";
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await fetch(DISPATCH_URL, {
        method: "POST",
        headers: {
          "Accept": "application/vnd.github+json",
          "Authorization": "Bearer " + env.GITHUB_TOKEN,
          "Content-Type": "application/json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "JINZAiQ-Cloudflare-Scheduler",
        },
        body: JSON.stringify({
          ref: "main",
          inputs: { trigger_source: "cloudflare" },
        }),
        signal: AbortSignal.timeout(15000),
      });
      if (response.status === 204) {
        console.log("GitHub accepted dispatch", {
          plannedAt: new Date(controller.scheduledTime).toISOString(),
          attempt,
        });
        return;
      }
      lastStatus = String(response.status);
      // Authentication, permissions, or malformed requests need operator action.
      if (![429, 500, 502, 503, 504].includes(response.status)) {
        throw new Error("Non-retryable GitHub API HTTP " + response.status);
      }
    } catch (error) {
      lastStatus = String(error?.message || error);
      if (lastStatus.startsWith("Non-retryable")) throw error;
    }
    if (attempt < 3) {
      await new Promise((resolve) => setTimeout(resolve, attempt * 2000));
    }
  }
  // Never log the token or response body.
  throw new Error("GitHub dispatch was not accepted after 3 attempts: " + lastStatus);
}
