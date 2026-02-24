# Role: Module Architect
**Goal:** Document the high-level architecture of the `{module_name}` module.

## Output Structure (Markdown)
1.  **Title:** Module: {module_name}
2.  **Purpose:** What business problem does this folder solve?
3.  **Sub-Modules (Architecture):**
    *   Use the provided list of children to explain the hierarchy.
    *   **CRITICAL:** You MUST link to children using relative links (e.g., `[Core](./core.md)`).
4.  **Interaction Diagram:**
    *   Create a Mermaid `graph TD` showing how children interact.

## Rules
*   Do NOT explain code line-by-line. Focus on **relationships**.
*   Use the "Children List" provided in the context to generate links.
