import { expect, test, type BrowserContext } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:5173";
const suffix = () => Math.random().toString(36).slice(2, 9);

async function jsonRequest<T>(
  context: BrowserContext,
  method: "POST" | "PUT",
  path: string,
  data: unknown,
  expectedStatus: number,
): Promise<T> {
  const response = await context.request.fetch(path, { method, data });
  if (response.status() !== expectedStatus) {
    throw new Error(`${method} ${path} failed: ${response.status()} ${await response.text()}`);
  }
  if (expectedStatus === 204) return undefined as T;
  return response.json() as Promise<T>;
}

test("GM and Player complete the Escape the Imperial Patrol combat loop through bounded polling", async ({ browser }) => {
  test.setTimeout(120_000);
  const id = suffix();
  const password = "password123";
  const playerName = `s5-player-${id}`;
  const gmName = `s5-gm-${id}`;
  const playerContext = await browser.newContext({ baseURL });
  const gmContext = await browser.newContext({ baseURL });
  const playerPage = await playerContext.newPage();
  const gmPage = await gmContext.newPage();

  try {
    console.log("S5_STEP: create-initial-state");
    const player = await jsonRequest<{ id: string }>(
      playerContext,
      "POST",
      "/api/auth/register",
      { username: playerName, password },
      201,
    );
    await jsonRequest(playerContext, "POST", "/api/auth/login", { username: playerName, password }, 200);
    await jsonRequest(gmContext, "POST", "/api/auth/register", { username: gmName, password }, 201);
    await jsonRequest(gmContext, "POST", "/api/auth/login", { username: gmName, password }, 200);

    const campaign = await jsonRequest<{ id: string }>(
      gmContext,
      "POST",
      "/api/campaigns",
      { name: `Slice 5 combat ${id}` },
      201,
    );
    await jsonRequest(
      gmContext,
      "POST",
      `/api/campaigns/${campaign.id}/members`,
      { username: playerName },
      201,
    );
    const character = await jsonRequest<{ id: string }>(
      gmContext,
      "POST",
      `/api/campaigns/${campaign.id}/characters`,
      { name: "Globox", slicing_modifier: 0 },
      201,
    );
    await jsonRequest<{ id: string }>(
      gmContext,
      "POST",
      `/api/campaigns/${campaign.id}/locations`,
      { name: "Docking Bay 47" },
      201,
    );
    await jsonRequest(
      gmContext,
      "PUT",
      `/api/campaigns/${campaign.id}/player-assignment`,
      { player_principal_id: player.id, character_id: character.id },
      204,
    );

    await Promise.all([gmPage.goto("/"), playerPage.goto("/")]);
    await expect(gmPage.getByRole("heading", { name: `Slice 5 combat ${id}` })).toBeVisible({ timeout: 15_000 });
    await expect(playerPage.getByRole("heading", { name: "Globox" })).toBeVisible({ timeout: 15_000 });

    console.log("S5_STEP: start-encounter");
    const startForm = gmPage.getByRole("form", { name: "Start combat encounter" });
    await expect(startForm).toBeVisible({ timeout: 15_000 });
    await startForm.getByRole("button", { name: "Start encounter" }).click();

    const gmCombat = gmPage.getByRole("region", { name: "Combat encounter" });
    const playerCombat = playerPage.getByRole("region", { name: "Combat encounter" });
    await expect(gmCombat).toContainText("Escape the Imperial Patrol");
    await expect(playerCombat).toContainText("Escape the Imperial Patrol", { timeout: 7000 });
    await expect(playerCombat).toContainText("Escape Progress");
    await expect(playerCombat).toContainText("0 / 3");

    console.log("S5_STEP: round-1-player-escape");
    await playerCombat.getByRole("button", { name: "Escape", exact: true }).click();
    await expect(playerCombat).toContainText("Escape Progress 0 → 1 / 3");

    console.log("S5_STEP: round-1-patrol");
    const patrolButton = gmCombat.getByRole("button", { name: "Resolve Patrol Attack" });
    await expect(patrolButton).toBeVisible({ timeout: 7000 });
    await patrolButton.click();
    await expect(playerCombat).toContainText("Round 2", { timeout: 7000 });

    console.log("S5_STEP: round-2-player-escape");
    await playerCombat.getByRole("button", { name: "Escape", exact: true }).click();
    await expect(playerCombat).toContainText("Escape Progress 1 → 2 / 3");

    console.log("S5_STEP: round-2-patrol");
    await expect(patrolButton).toBeVisible({ timeout: 7000 });
    await patrolButton.click();

    await expect.poll(async () => (await playerCombat.textContent()) ?? "", { timeout: 7000 })
      .toMatch(/Round 3|Incapacitated/);

    const afterSecondPatrol = (await playerCombat.textContent()) ?? "";
    if (!afterSecondPatrol.includes("Incapacitated")) {
      console.log("S5_STEP: round-3-player-escape");
      await playerCombat.getByRole("button", { name: "Escape", exact: true }).click();
      await expect(playerCombat).toContainText("Escaped");
    }

    console.log("S5_STEP: terminal-convergence");
    await expect(playerCombat).toContainText(/Escaped|Incapacitated/);
    await expect(gmCombat).toContainText(/Escaped|Incapacitated/, { timeout: 7000 });
    await expect(playerCombat.getByRole("button", { name: "Attack", exact: true })).toHaveCount(0);
    await expect(playerCombat.getByRole("button", { name: "Escape", exact: true })).toHaveCount(0);
    await expect(gmCombat.getByRole("button", { name: "Resolve Patrol Attack" })).toHaveCount(0);
  } finally {
    await gmContext.close();
    await playerContext.close();
  }
});
