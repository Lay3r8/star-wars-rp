import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:5173";
const suffix = () => Math.random().toString(36).slice(2, 9);
const claim = "The confiscated shipment was transferred to Dock 47.";
const intent = "Discover where the confiscated shipment was transferred.";
const visibleRisk = "On failure, Imperial security notices the intrusion.";
const hiddenRisk = "Imperial counter-intelligence silently fingerprints the intrusion.";

type Scenario = {
  gmContext: BrowserContext;
  playerContext: BrowserContext;
  gmPage: Page;
  playerPage: Page;
};

async function jsonRequest<T>(
  context: BrowserContext,
  method: "POST" | "PUT",
  path: string,
  data: unknown,
  expectedStatus: number,
): Promise<T> {
  const response = await context.request.fetch(path, { method, data });
  if (response.status() !== expectedStatus) {
    throw new Error(
      `${method} ${path} failed: ${response.status()} ${await response.text()}`,
    );
  }
  if (expectedStatus === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function prepareScenario(
  browser: Browser,
  label: string,
  riskVisibility: "GM_ONLY" | "PLAYER_VISIBLE",
  createViaUi = true,
): Promise<Scenario> {
  const id = suffix();
  const playerName = `s4-player-${label}-${id}`;
  const gmName = `s4-gm-${label}-${id}`;
  const password = "password123";

  const playerContext = await browser.newContext({ baseURL });
  const gmContext = await browser.newContext({ baseURL });
  const playerPage = await playerContext.newPage();
  const gmPage = await gmContext.newPage();

  console.log("S4_STEP: create-initial-state");

  const player = await jsonRequest<{ id: string; username: string }>(
    playerContext,
    "POST",
    "/api/auth/register",
    { username: playerName, password },
    201,
  );
  await jsonRequest(
    playerContext,
    "POST",
    "/api/auth/login",
    { username: playerName, password },
    200,
  );

  await jsonRequest(
    gmContext,
    "POST",
    "/api/auth/register",
    { username: gmName, password },
    201,
  );
  await jsonRequest(
    gmContext,
    "POST",
    "/api/auth/login",
    { username: gmName, password },
    200,
  );

  const campaign = await jsonRequest<{ id: string }>(
    gmContext,
    "POST",
    "/api/campaigns",
    { name: `Slice 4 ${label} ${id}` },
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
    { name: "Globox", slicing_modifier: 2 },
    201,
  );
  const location = await jsonRequest<{ id: string }>(
    gmContext,
    "POST",
    `/api/campaigns/${campaign.id}/locations`,
    { name: "Imperial Cargo Terminal" },
    201,
  );
  const fragment = await jsonRequest<{ id: string }>(
    gmContext,
    "POST",
    `/api/campaigns/${campaign.id}/knowledge-fragments`,
    { claim_text: claim, gm_veracity: "TRUE" },
    201,
  );
  await jsonRequest(
    gmContext,
    "PUT",
    `/api/campaigns/${campaign.id}/player-assignment`,
    { player_principal_id: player.id, character_id: character.id },
    204,
  );

  if (createViaUi) {
    // Live-path acceptance: both principals are already in their campaign workspaces
    // before the GM creates the request, so Player discovery is proven by polling.
    await Promise.all([gmPage.goto("/"), playerPage.goto("/")]);
    await expect(playerPage.getByRole("heading", { name: "Globox" })).toBeVisible({
      timeout: 15_000,
    });

    const resolution = gmPage.getByRole("region", { name: "Resolution adjudication" });
    await expect(
      resolution.getByRole("button", { name: "Create pre-bound resolution" }),
    ).toBeEnabled({ timeout: 15_000 });

    console.log("S4_STEP: configure-resolution");
    await resolution.getByLabel("Roll authority").selectOption("PLAYER");
    await resolution.getByLabel("Risk visibility").selectOption(riskVisibility);

    console.log("S4_STEP: submit-resolution");
    await resolution.getByRole("button", { name: "Create pre-bound resolution" }).click();
    await expect(
      gmPage.getByRole("region", { name: "Current resolution" }),
    ).toContainText("Waiting for Player Roll");
  } else {
    // Security-path fixture: creation UI is already covered above. Create the same
    // accepted contract through the existing GM API, then test only Player-safe UI.
    await jsonRequest(
      gmContext,
      "POST",
      `/api/campaigns/${campaign.id}/resolutions`,
      {
        actor_character_id: character.id,
        context_location_id: location.id,
        intent,
        risk: riskVisibility === "PLAYER_VISIBLE" ? visibleRisk : hiddenRisk,
        roll_authority: "PLAYER",
        risk_visibility: riskVisibility,
        dc: 100,
        success_recipient_character_id: character.id,
        success_fragment_id: fragment.id,
      },
      201,
    );
    await Promise.all([gmPage.goto("/"), playerPage.goto("/")]);
    await expect(playerPage.getByRole("heading", { name: "Globox" })).toBeVisible({
      timeout: 15_000,
    });
  }

  return { gmContext, playerContext, gmPage, playerPage };
}

async function closeScenario(value: Scenario) {
  await value.gmContext.close();
  await value.playerContext.close();
}

test("Player rolls a GM request and both sides converge through polling without global Refresh", async ({ browser }) => {
  test.setTimeout(120_000);
  const scenario = await prepareScenario(browser, "live", "PLAYER_VISIBLE");
  try {
    const pending = scenario.playerPage.getByRole("region", { name: "Pending roll request" });

    // Request appears through bounded polling; no global Refresh or browser reload.
    await expect(pending).toBeVisible({ timeout: 7000 });
    await expect(pending).toContainText("Globox");
    await expect(pending).toContainText("Slicing");
    await expect(pending).toContainText("Imperial Cargo Terminal");
    await expect(pending).toContainText(intent);
    await expect(pending).toContainText(visibleRisk);
    await expect(pending).not.toContainText("DC");
    await expect(pending).not.toContainText(claim);

    const gmCurrent = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await expect(gmCurrent).toContainText("Waiting for Player Roll");
    await expect(gmCurrent.getByRole("button", { name: "Roll", exact: true })).toHaveCount(0);

    await pending.getByRole("button", { name: "Roll", exact: true }).click();

    await expect(pending.locator(".mechanical-evidence")).toBeVisible();
    await expect(pending).toContainText("Waiting for GM adjudication");

    const mechanicalText = await pending
      .getByText(/Mechanical result: (SUCCESS|FAILURE)/)
      .textContent();
    const mechanicalResult = mechanicalText?.includes("SUCCESS") ? "SUCCESS" : "FAILURE";
    const overrideOutcome = mechanicalResult === "SUCCESS" ? "FAILURE" : "SUCCESS";

    // GM observes the same Player-generated mechanical result through bounded polling.
    await expect(gmCurrent.locator(".mechanical-evidence")).toBeVisible({ timeout: 7000 });
    await expect(gmCurrent).toContainText(`Mechanical result: ${mechanicalResult}`);

    // Exercise Slice 3 Override after a Player-triggered Roll.
    await gmCurrent.getByRole("button", { name: "Override outcome…" }).click();
    await gmCurrent
      .getByRole("button", {
        name: overrideOutcome === "SUCCESS" ? "Finalize as Success" : "Finalize as Failure",
      })
      .click();

    // Player sees finalized adjudication through polling; still no global Refresh.
    const finalized = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(finalized).toBeVisible({ timeout: 7000 });
    await expect(finalized).toContainText(`Mechanical result: ${mechanicalResult}`);
    await expect(finalized).toContainText(
      `Final outcome: ${overrideOutcome} (GM adjudication)`,
    );
    if (overrideOutcome === "SUCCESS") {
      await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
    }

    // Regression: an existing finalized summary must not stop request discovery.
    // Create another PLAYER-authority resolution while the Player remains on the
    // same open workspace, then prove it appears through polling without reload.
    const resolutionWorkspace = scenario.gmPage.getByRole("region", {
      name: "Resolution adjudication",
    });
    await resolutionWorkspace.getByLabel("Roll authority").selectOption("PLAYER");
    await resolutionWorkspace
      .getByRole("button", { name: "Create pre-bound resolution" })
      .click();

    await expect(pending).toBeVisible({ timeout: 7000 });
    await expect(pending.getByRole("button", { name: "Roll", exact: true })).toBeVisible();
  } finally {
    await closeScenario(scenario);
  }
});

test("GM-only Risk, DC and success claim stay hidden and Player has no GM mutation controls", async ({ browser }) => {
  test.setTimeout(120_000);
  const scenario = await prepareScenario(browser, "hidden", "GM_ONLY", false);
  try {
    const pending = scenario.playerPage.getByRole("region", { name: "Pending roll request" });
    await expect(pending).toBeVisible({ timeout: 7000 });
    await expect(pending).toContainText(intent);
    await expect(pending).not.toContainText(hiddenRisk);
    await expect(pending).not.toContainText("Known stakes");
    await expect(pending).not.toContainText("DC");
    await expect(pending).not.toContainText(claim);
    await expect(scenario.playerPage.getByRole("button", { name: /Finalize|Override|Correct/ })).toHaveCount(0);

    const gmCurrent = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await expect(gmCurrent.getByRole("button", { name: "Roll", exact: true })).toHaveCount(0);
    await expect(gmCurrent).toContainText(hiddenRisk);
  } finally {
    await closeScenario(scenario);
  }
});
