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

test("GM prepares, finds, edits and reveals a Contact", async ({ browser }) => {
  const id = suffix();
  const playerName = `contact-player-${id}`;
  const gmName = `contact-gm-${id}`;
  const claim = "A customs audit is scheduled for Dock 47 tomorrow at 06:00.";

  const playerContext = await browser.newContext();
  const playerPage = await playerContext.newPage();
  await register(playerPage, playerName);
  await playerPage.getByRole("button", { name: "Logout" }).click();

  const gmContext = await browser.newContext();
  const gmPage = await gmContext.newPage();
  await register(gmPage, gmName);

  await gmPage.getByLabel("New campaign").fill(`Contacts ${id}`);
  await gmPage.getByRole("button", { name: "Create as GM" }).click();

  // Slice 2 starts with these fixtures already present. The legacy setup surface is
  // used only to manufacture that accepted precondition in E2E.
  await gmPage.getByText("Slice 1 proof setup").click();
  await gmPage.getByLabel("Registered username").fill(playerName);
  await gmPage.getByRole("button", { name: "Add to campaign" }).click();
  await expect(gmPage.locator("ul.compact li", { hasText: playerName })).toBeVisible();

  await gmPage.getByLabel("Character name").fill("Ryn Tal");
  await gmPage.getByRole("button", { name: "Create character" }).click();
  await expect(gmPage.getByLabel("Character").locator("option")).toContainText(["Ryn Tal"]);

  await gmPage.getByLabel("Location name").fill("Dock 47");
  await gmPage.getByRole("button", { name: "Create location" }).click();
  await expect(gmPage.getByText("Dock 47", { exact: true })).toBeVisible();

  await gmPage.getByRole("button", { name: "Assign" }).click();
  await gmPage.getByText("Slice 1 proof setup").click();

  const contacts = gmPage.getByRole("region", { name: "Contacts" });
  await contacts.getByLabel("Name").fill("Nira Voss");
  await contacts.getByLabel("Role").fill("Imperial dock clerk and discreet informant");
  await contacts.getByLabel("GM note").fill("Keeps a low profile around customs officers.");
  await contacts.getByLabel("Information this Contact knows").fill(claim);
  await contacts.getByLabel("Truth status").selectOption("TRUE");
  await contacts.getByRole("button", { name: "Save Contact" }).click();
  await expect(contacts.getByText("Contact saved.")).toBeVisible();

  // Edit accepted canonical state.
  await gmPage.getByRole("region", { name: "Contact summary" }).getByRole("button", { name: "Edit" }).click();
  await contacts.getByLabel("Role").fill("Senior Imperial dock clerk and discreet informant");
  await contacts.getByLabel("GM note").fill("Now watches customs traffic closely.");
  await contacts.getByRole("button", { name: "Save changes" }).click();
  await expect(contacts.getByText("Contact changes saved.")).toBeVisible();

  await gmPage.reload();

  // Search by role term after reload; one result stays selectable rather than auto-opening.
  const reloadedContacts = gmPage.getByRole("region", { name: "Contacts" });
  const search = reloadedContacts.getByLabel("Search name or role");
  await search.fill("dock");
  const niraResult = reloadedContacts.getByRole("option", { name: /Nira Voss/ });
  await expect(niraResult).toBeVisible();
  await expect(niraResult).toContainText("Dock 47");
  await niraResult.click();

  const summary = gmPage.getByRole("region", { name: "Contact summary" });
  await expect(summary.getByRole("heading", { name: "Nira Voss" })).toBeVisible();
  await expect(summary.getByText("Senior Imperial dock clerk and discreet informant", { exact: false })).toBeVisible();
  await expect(summary.getByText(claim, { exact: true })).toBeVisible();

  // Player sees no hidden prepared information before explicit Reveal.
  await playerPage.getByLabel("Username").fill(playerName);
  await playerPage.getByLabel("Password").fill("password123");
  await playerPage.getByRole("button", { name: "Login" }).click();
  await expect(playerPage.getByText("No disclosed knowledge yet.")).toBeVisible();
  await expect(playerPage.getByText(claim, { exact: true })).toHaveCount(0);

  await summary.getByRole("button", { name: "Reveal…" }).click();
  await expect(summary.getByText("Recipient:")).toBeVisible();
  await expect(summary.getByText("Ryn Tal", { exact: true })).toBeVisible();
  await expect(summary.locator(".reveal-preview").getByText(claim, { exact: true })).toBeVisible();
  await summary.getByRole("button", { name: "Confirm Reveal" }).click();
  await expect(summary.getByText("Revealed to Ryn Tal.")).toBeVisible();

  await playerPage.reload();
  await expect(playerPage.getByText(claim, { exact: true })).toBeVisible();

  // Reload preserves both Contact and disclosure state.
  await gmPage.reload();
  const finalContacts = gmPage.getByRole("region", { name: "Contacts" });
  await finalContacts.getByLabel("Search name or role").fill("Nira");
  await finalContacts.getByRole("option", { name: /Nira Voss/ }).click();
  await expect(gmPage.getByRole("region", { name: "Contact summary" }).getByText(claim, { exact: true })).toBeVisible();

  await gmContext.close();
  await playerContext.close();
});
