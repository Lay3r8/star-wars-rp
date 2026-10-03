import { expect, test } from "@playwright/test";

const suffix = () => Math.random().toString(36).slice(2, 9);

async function register(page: import("@playwright/test").Page, username: string) {
  await page.goto("/");
  await page.getByRole("button", { name: "Create a principal" }).click();
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Register & login" }).click();
  await expect(page.getByText(username)).toBeVisible();
}

async function setup(
  page: import("@playwright/test").Page,
  playerName: string,
  campaignName: string,
  dc: string,
) {
  await page.getByLabel("New campaign").fill(campaignName);
  await page.getByRole("button", { name: "Create as GM" }).click();
  await page.getByText("Slice 1 proof setup").click();

  await page.getByLabel("Registered username").fill(playerName);
  await page.getByRole("button", { name: "Add to campaign" }).click();
  await expect(page.locator("ul.compact li", { hasText: playerName })).toBeVisible();

  await page.getByLabel("Character name").fill("Kara Venn");
  await page.getByRole("button", { name: "Create character" }).click();
  await page.getByRole("button", { name: "Create location" }).click();
  await page.getByRole("button", { name: "Create secret" }).click();
  await page.getByRole("button", { name: "Assign" }).click();

  await page.getByLabel("DC").fill(dc);
  await page.getByRole("button", { name: "Create pre-bound resolution" }).click();
}

test("success roll waits for GM Finalize before disclosure", async ({ browser }) => {
  const id = suffix();
  const playerName = `player-${id}`;
  const gmName = `gm-${id}`;

  const playerContext = await browser.newContext();
  const playerPage = await playerContext.newPage();
  await register(playerPage, playerName);
  await playerPage.getByRole("button", { name: "Logout" }).click();

  const gmContext = await browser.newContext();
  const gmPage = await gmContext.newPage();
  await register(gmPage, gmName);
  await setup(gmPage, playerName, `Campaign ${id}`, "1");

  await gmPage.getByRole("button", { name: "Roll" }).click();
  const current = gmPage.getByRole("region", { name: "Current resolution" });
  await expect(current.locator(".mechanical-evidence")).toContainText("Mechanical result: SUCCESS");
  await expect(current.getByRole("button", { name: "Finalize Success" })).toBeVisible();

  await playerPage.getByLabel("Username").fill(playerName);
  await playerPage.getByLabel("Password").fill("password123");
  await playerPage.getByRole("button", { name: "Login" }).click();
  await expect(playerPage.getByText("No disclosed knowledge yet.")).toBeVisible();
  await expect(playerPage.getByRole("region", { name: "Latest finalized resolution" })).toHaveCount(0);

  await current.getByRole("button", { name: "Finalize Success" }).click();
  await playerPage.getByRole("button", { name: "Refresh" }).click();
  await expect(playerPage.getByText("The confiscated shipment was transferred to Dock 47.")).toBeVisible();
  await expect(playerPage.getByRole("region", { name: "Latest finalized resolution" })).toContainText("Final outcome: SUCCESS");

  await gmContext.close();
  await playerContext.close();
});

test("failure finalizes with the declared Risk as concrete consequence", async ({ page }) => {
  const id = suffix();
  const playerName = `player-fail-${id}`;
  const gmName = `gm-fail-${id}`;

  await register(page, playerName);
  await page.getByRole("button", { name: "Logout" }).click();
  await register(page, gmName);
  await setup(page, playerName, `Failure ${id}`, "100");

  await page.getByRole("button", { name: "Roll" }).click();
  const current = page.getByRole("region", { name: "Current resolution" });
  await expect(current.locator(".mechanical-evidence")).toContainText("Mechanical result: FAILURE");
  await current.getByRole("button", { name: "Finalize Failure" }).click();
  await expect(current).toContainText("Final outcome: FAILURE");
  await expect(current).toContainText("On failure, Imperial security notices the intrusion.");

  await page.reload();
  await expect(page.getByRole("region", { name: "Current resolution" })).toContainText("Final outcome: FAILURE");
});
