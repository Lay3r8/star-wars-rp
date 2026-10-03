import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";

const suffix = () => Math.random().toString(36).slice(2, 9);
const claim = "The confiscated shipment was transferred to Dock 47.";
const intent = "Obtain information about Senator Traitrus.";
const visibleRisk = "Vic may realize you are investigating him.";
const hiddenRisk = "Imperial counter-intelligence silently fingerprints the intrusion.";

async function register(page: Page, username: string) {
  await page.goto("/");
  await page.getByRole("button", { name: "Create a principal" }).click();
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Register & login" }).click();
}

type Scenario = {
  gmContext: BrowserContext;
  playerContext: BrowserContext;
  gmPage: Page;
  playerPage: Page;
};

async function prepareScenario(
  browser: Browser,
  label: string,
  riskVisibility: "GM_ONLY" | "PLAYER_VISIBLE",
): Promise<Scenario> {
  const id = suffix();
  const playerName = `s4-player-${label}-${id}`;
  const gmName = `s4-gm-${label}-${id}`;

  const playerContext = await browser.newContext();
  const playerPage = await playerContext.newPage();
  playerPage.setDefaultTimeout(10_000);
  await register(playerPage, playerName);
  await playerPage.getByRole("button", { name: "Logout" }).click();

  const gmContext = await browser.newContext();
  const gmPage = await gmContext.newPage();
  gmPage.setDefaultTimeout(10_000);
  await register(gmPage, gmName);

  await gmPage.getByLabel("New campaign").fill(`Slice 4 ${label} ${id}`);
  await gmPage.getByRole("button", { name: "Create as GM" }).click();
  await gmPage.getByText("Slice 1 proof setup").click();

  await gmPage.getByLabel("Registered username").fill(playerName);
  await gmPage.getByRole("button", { name: "Add to campaign" }).click();
  await gmPage.getByLabel("Character name").fill("Globox");
  await gmPage.getByRole("button", { name: "Create character" }).click();
  await gmPage.getByRole("button", { name: "Create location" }).click();
  await gmPage.getByRole("button", { name: "Create secret" }).click();
  await gmPage.getByRole("button", { name: "Assign" }).click();
  await gmPage.getByText("Slice 1 proof setup").click();

  // Player is already in the workspace before the GM creates the request.
  await playerPage.getByLabel("Username").fill(playerName);
  await playerPage.getByLabel("Password").fill("password123");
  await playerPage.getByRole("button", { name: "Login" }).click();
  await expect(playerPage.getByRole("heading", { name: "Globox" })).toBeVisible();

  const resolution = gmPage.getByRole("region", { name: "Resolution adjudication" });
  await resolution.getByLabel("Roll authority").selectOption("PLAYER");
  await resolution.getByLabel("Risk visibility").selectOption(riskVisibility);
  await resolution.getByLabel("Intent").fill(intent);
  await resolution.getByLabel("Risk", { exact: true }).fill(
    riskVisibility === "PLAYER_VISIBLE" ? visibleRisk : hiddenRisk,
  );
  await resolution.getByLabel("DC").fill("100");
  await resolution.getByRole("button", { name: "Create pre-bound resolution" }).click();

  return { gmContext, playerContext, gmPage, playerPage };
}

async function closeScenario(value: Scenario) {
  await value.gmContext.close();
  await value.playerContext.close();
}

test("Player rolls a GM request and both sides converge through polling without global Refresh", async ({ browser }) => {
  test.setTimeout(60_000);
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
    await expect(pending).toContainText("Mechanical result: FAILURE");
    await expect(pending).toContainText("Waiting for GM adjudication");

    // GM observes the Player-generated mechanical result through its own bounded polling.
    await expect(gmCurrent.locator(".mechanical-evidence")).toBeVisible({ timeout: 7000 });
    await expect(gmCurrent).toContainText("Mechanical result: FAILURE");

    // Exercise Slice 3 Override after a Player-triggered Roll.
    await gmCurrent.getByRole("button", { name: "Override outcome…" }).click();
    await gmCurrent.getByLabel(/Override reason/).fill("The cached record is still readable.");
    await gmCurrent.getByRole("button", { name: "Finalize as Success" }).click();

    // Player sees finalized adjudication through polling; still no global Refresh.
    const finalized = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(finalized).toBeVisible({ timeout: 7000 });
    await expect(finalized).toContainText("Mechanical result: FAILURE");
    await expect(finalized).toContainText("Final outcome: SUCCESS (GM adjudication)");
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
  } finally {
    await closeScenario(scenario);
  }
});

test("GM-only Risk, DC and success claim stay hidden and Player has no GM mutation controls", async ({ browser }) => {
  test.setTimeout(60_000);
  const scenario = await prepareScenario(browser, "hidden", "GM_ONLY");
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
