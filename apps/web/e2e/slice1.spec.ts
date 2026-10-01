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

test("success reveals only after GM Apply", async ({ browser }) => {
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

  await gmPage.getByLabel("New campaign").fill(`Campaign ${id}`);
  await gmPage.getByRole("button", { name: "Create as GM" }).click();

  await gmPage.getByLabel("Registered username").fill(playerName);
  await gmPage.getByRole("button", { name: "Add to campaign" }).click();
  await expect(gmPage.getByText(playerName, { exact: true })).toBeVisible();

  await gmPage.getByLabel("Character name").fill("Kara Venn");
  await gmPage.getByRole("button", { name: "Create character" }).click();
  await expect(gmPage.getByRole("option", { name: "Kara Venn" })).toBeVisible();
  await gmPage.getByRole("button", { name: "Create location" }).click();
  await expect(gmPage.getByText("Imperial Cargo Terminal", { exact: true })).toBeVisible();
  await gmPage.getByRole("button", { name: "Create secret" }).click();
  await expect(gmPage.getByText("The confiscated shipment was transferred to Dock 47.", { exact: true })).toBeVisible();

  await gmPage.getByRole("button", { name: "Assign" }).click();

  await gmPage.getByLabel("DC").fill("1");
  await gmPage.getByRole("button", { name: "Create pre-bound resolution" }).click();
  await gmPage.getByRole("button", { name: "Roll" }).click();
  await expect(gmPage.getByText("SUCCESS", { exact: true })).toBeVisible();

  await playerPage.getByLabel("Username").fill(playerName);
  await playerPage.getByLabel("Password").fill("password123");
  await playerPage.getByRole("button", { name: "Login" }).click();
  await expect(playerPage.getByText("No disclosed knowledge yet.")).toBeVisible();

  await gmPage.getByRole("button", { name: "Apply reveal" }).click();
  await playerPage.getByRole("button", { name: "Refresh" }).click();
  await expect(playerPage.getByText("The confiscated shipment was transferred to Dock 47.")).toBeVisible();

  await gmContext.close();
  await playerContext.close();
});

test("failure ends with concrete GM adjudication and Close", async ({ page }) => {
  const id = suffix();
  const playerName = `player-fail-${id}`;
  const gmName = `gm-fail-${id}`;

  await register(page, playerName);
  await page.getByRole("button", { name: "Logout" }).click();
  await register(page, gmName);

  await page.getByLabel("New campaign").fill(`Failure ${id}`);
  await page.getByRole("button", { name: "Create as GM" }).click();
  await page.getByLabel("Registered username").fill(playerName);
  await page.getByRole("button", { name: "Add to campaign" }).click();
  await expect(page.getByText(playerName, { exact: true })).toBeVisible();
  await page.getByLabel("Character name").fill("Kara Venn");
  await page.getByRole("button", { name: "Create character" }).click();
  await expect(page.getByRole("option", { name: "Kara Venn" })).toBeVisible();
  await page.getByRole("button", { name: "Create location" }).click();
  await expect(page.getByText("Imperial Cargo Terminal", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Create secret" }).click();
  await expect(page.getByText("The confiscated shipment was transferred to Dock 47.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Assign" }).click();

  await page.getByLabel("DC").fill("100");
  await page.getByRole("button", { name: "Create pre-bound resolution" }).click();
  await page.getByRole("button", { name: "Roll" }).click();
  await expect(page.getByText("FAILURE", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Close failed resolution" }).click();
  await expect(page.getByText("Resolution closed.")).toBeVisible();
  await expect(page.getByText("Imperial security logs the intrusion.")).toBeVisible();
});
