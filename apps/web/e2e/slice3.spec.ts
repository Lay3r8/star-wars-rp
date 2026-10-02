import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";

const suffix = () => Math.random().toString(36).slice(2, 9);
const claim = "The confiscated shipment was transferred to Dock 47.";

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
  playerName: string;
};

async function prepareScenario(browser: Browser, label: string, dc: "1" | "100"): Promise<Scenario> {
  const id = suffix();
  const playerName = `s3-player-${label}-${id}`;
  const gmName = `s3-gm-${label}-${id}`;

  const playerContext = await browser.newContext();
  const playerPage = await playerContext.newPage();
  await register(playerPage, playerName);
  await playerPage.getByRole("button", { name: "Logout" }).click();

  const gmContext = await browser.newContext();
  const gmPage = await gmContext.newPage();
  await register(gmPage, gmName);

  await gmPage.getByLabel("New campaign").fill(`Slice 3 ${label} ${id}`);
  await gmPage.getByRole("button", { name: "Create as GM" }).click();
  await gmPage.getByText("Slice 1 proof setup").click();

  await gmPage.getByLabel("Registered username").fill(playerName);
  await gmPage.getByRole("button", { name: "Add to campaign" }).click();
  await gmPage.getByLabel("Character name").fill("Kara Venn");
  await gmPage.getByRole("button", { name: "Create character" }).click();
  await gmPage.getByRole("button", { name: "Create location" }).click();
  await gmPage.getByRole("button", { name: "Create secret" }).click();
  await gmPage.getByRole("button", { name: "Assign" }).click();

  await gmPage.getByLabel("DC").fill(dc);
  await gmPage.getByRole("button", { name: "Create pre-bound resolution" }).click();
  await gmPage.getByRole("button", { name: "Roll" }).click();

  await playerPage.getByLabel("Username").fill(playerName);
  await playerPage.getByLabel("Password").fill("password123");
  await playerPage.getByRole("button", { name: "Login" }).click();

  return { gmContext, playerContext, gmPage, playerPage, playerName };
}

async function closeScenario(value: Scenario) {
  await value.gmContext.close();
  await value.playerContext.close();
}

test("normal mechanical success finalizes and becomes Player-visible", async ({ browser }) => {
  const scenario = await prepareScenario(browser, "normal", "1");
  try {
    const current = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await expect(current.getByText(/Mechanical result:/)).toContainText("SUCCESS");
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toHaveCount(0);

    await current.getByRole("button", { name: "Finalize Success" }).click();
    await scenario.playerPage.reload();

    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
    const summary = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(summary).toContainText("Mechanical result: SUCCESS");
    await expect(summary).toContainText("Final outcome: SUCCESS");
  } finally {
    await closeScenario(scenario);
  }
});

test("mechanical failure can be overridden to final success", async ({ browser }) => {
  const scenario = await prepareScenario(browser, "override-fs", "100");
  try {
    const current = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await expect(current.getByText(/Mechanical result:/)).toContainText("FAILURE");
    await current.getByRole("button", { name: "Override outcome…" }).click();
    await current.getByLabel(/Override reason/).fill("Cached records remain readable.");
    await current.getByRole("button", { name: "Finalize as Success" }).click();

    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
    const summary = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(summary).toContainText("Mechanical result: FAILURE");
    await expect(summary).toContainText("Final outcome: SUCCESS (GM adjudication)");
  } finally {
    await closeScenario(scenario);
  }
});

test("mechanical success can be overridden to final failure", async ({ browser }) => {
  const scenario = await prepareScenario(browser, "override-sf", "1");
  try {
    const current = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await current.getByRole("button", { name: "Override outcome…" }).click();
    await current.getByLabel(/Override reason/).fill("The access token was a decoy.");
    await current.getByRole("button", { name: "Finalize as Failure" }).click();

    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toHaveCount(0);
    const summary = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(summary).toContainText("Mechanical result: SUCCESS");
    await expect(summary).toContainText("Final outcome: FAILURE (GM adjudication)");
  } finally {
    await closeScenario(scenario);
  }
});

test("final failure can be corrected to success", async ({ browser }) => {
  const scenario = await prepareScenario(browser, "correct-fs", "100");
  try {
    const current = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await current.getByRole("button", { name: "Finalize Failure" }).click();
    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toHaveCount(0);

    await current.getByRole("button", { name: "Correct outcome…" }).click();
    await current.getByLabel("Correction reason").fill("Reviewed the fiction after finalization.");
    await current.getByRole("button", { name: "Apply correction" }).click();

    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
    const summary = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(summary).toContainText("Final outcome: SUCCESS");
    await expect(summary).toContainText("Corrected.");
    await expect(summary).toContainText("Previously finalized as FAILURE");

    await scenario.gmPage.reload();
    await expect(scenario.gmPage.getByText("Resolution corrected FAILURE -> SUCCESS.")).toBeVisible();
  } finally {
    await closeScenario(scenario);
  }
});

test("correcting success to failure retains irreversible disclosed knowledge", async ({ browser }) => {
  const scenario = await prepareScenario(browser, "correct-sf", "1");
  try {
    const current = scenario.gmPage.getByRole("region", { name: "Current resolution" });
    await current.getByRole("button", { name: "Finalize Success" }).click();
    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();

    await current.getByRole("button", { name: "Correct outcome…" }).click();
    await expect(current.getByRole("note")).toContainText("This information has already been shown to Kara Venn.");
    await current.getByLabel("Correction reason").fill("The adjudication was corrected after disclosure.");
    await current.getByRole("button", { name: "Apply correction" }).click();

    await scenario.playerPage.reload();
    await expect(scenario.playerPage.getByText(claim, { exact: true })).toBeVisible();
    const summary = scenario.playerPage.getByRole("region", { name: "Latest finalized resolution" });
    await expect(summary).toContainText("Mechanical result: SUCCESS");
    await expect(summary).toContainText("Final outcome: FAILURE");
    await expect(summary).toContainText("Corrected.");
    await expect(summary).toContainText("Previously finalized as SUCCESS");
  } finally {
    await closeScenario(scenario);
  }
});
