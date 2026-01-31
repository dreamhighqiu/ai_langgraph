# Test Case Style Guide

Purpose: consistent, readable functional test cases that map to UI automation.

Structure (JSON-like):
- id: TC_XXX
- title: include the specific feature name (avoid generic "click button")
- priority: P0/P1/P2/P3
- preconditions: list
- steps: ordered, concrete actions with element names
- expected_result: clear, observable outcome

Coverage checklist:
- main flow (happy path)
- validation and error states
- boundary values when applicable
- permissions/visibility when applicable
- list/search/filter if present

Guidelines:
- Keep steps actionable and deterministic.
- Prefer business terminology from the UI.
- If reference cases exist, follow their naming and formatting.
