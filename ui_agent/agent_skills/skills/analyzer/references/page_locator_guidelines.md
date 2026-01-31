# Page Locator Guidelines

Goal: produce stable Playwright locators that survive UI changes.

Priority order (best first):
- data-testid or explicit test id attributes
- stable id
- name attribute for inputs
- aria-label or role + accessible name
- visible text with getByText / has-text

Avoid:
- nth-child or index-based selectors
- long or brittle CSS chains
- absolute XPath

Patterns (Playwright Java):
- page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Save"))
- page.getByText("Submit")
- page.locator("input[name='username']")
- page.locator("[data-testid='primary-save']")

Custom components:
- Use the custom tag plus :has-text when text exists.
  Example: page.locator("zeta-radio-button:has-text('Open')")

When in doubt, prefer the shortest locator that uniquely identifies the element.
