from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "3rdi" / "SKILL.md"
AGENT = ROOT / "skills" / "3rdi" / "agents" / "openai.yaml"


def split_skill() -> tuple[str, str]:
    text = SKILL.read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n(?P<body>.*)$", text, re.S)
    if not match:
        raise AssertionError("SKILL.md must contain YAML frontmatter")
    return match.group("frontmatter"), match.group("body")


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", frontmatter)
    if not match:
        raise AssertionError(f"missing frontmatter field: {key}")
    return match.group(1).strip()


class SkillOperatorContractTests(unittest.TestCase):
    def test_discovery_description_is_trigger_only(self) -> None:
        frontmatter, _ = split_skill()
        description = frontmatter_value(frontmatter, "description")

        self.assertTrue(
            description.startswith("Use when "),
            "description must begin with trigger conditions, not workflow",
        )
        self.assertLessEqual(
            len(description),
            500,
            "discovery metadata should stay compact enough to scan",
        )

    def test_loaded_skill_is_compact_and_routes_depth_to_references(self) -> None:
        _, body = split_skill()
        words = re.findall(r"\b\w+[\w'-]*\b", body)

        self.assertLessEqual(
            len(words),
            550,
            "the always-loaded skill should be an instrument panel, not the manual",
        )
        self.assertIn("references/operator-field-guide.md", body)
        self.assertIn("references/operator-evals.md", body)

    def test_constitution_keeps_authority_and_side_effect_boundaries_visible(self) -> None:
        _, body = split_skill()

        self.assertIn("projection != source != authority", body)
        self.assertIn("gate result != side effect", body)
        self.assertIn("relevance != causation", body)

    def test_openai_entrypoint_is_short_and_observer_local(self) -> None:
        agent = AGENT.read_text(encoding="utf-8")
        match = re.search(r'(?m)^\s*default_prompt:\s*"([^"]+)"$', agent)
        self.assertIsNotNone(match, "openai.yaml must expose a quoted default_prompt")
        prompt = match.group(1)

        self.assertIn("$3rdi", prompt)
        self.assertIn("observer", prompt.lower())
        self.assertLessEqual(len(prompt), 160)
        self.assertNotIn("LOCATE", prompt)
        self.assertNotIn("PRESSURE", prompt)


if __name__ == "__main__":
    unittest.main()
