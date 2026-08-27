from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "3rdi" / "SKILL.md"
AGENT = ROOT / "skills" / "3rdi" / "agents" / "openai.yaml"
DEVELOPMENT_CASES = ROOT / "evals" / "discovery-cases.json"
HOLDOUT_CASES = ROOT / "evals" / "holdout-cases.json"
ALLOWED_MODES = {"CUT", "PARALLAX", "REINTERPRET", "GATE", "LAB"}


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


def load_eval(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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

    def test_eval_catalogs_are_separate_and_well_formed(self) -> None:
        development = load_eval(DEVELOPMENT_CASES)
        holdout = load_eval(HOLDOUT_CASES)

        self.assertEqual(development["schema"], "3rdi.operator-eval/v0")
        self.assertEqual(holdout["schema"], "3rdi.operator-eval/v0")
        self.assertEqual(development["set"], "development")
        self.assertEqual(holdout["set"], "holdout")

        development_prompts = {case["prompt"] for case in development["cases"]}
        holdout_prompts = {case["prompt"] for case in holdout["cases"]}
        self.assertTrue(development_prompts.isdisjoint(holdout_prompts))

        all_ids: list[str] = []
        for catalog in (development, holdout):
            self.assertGreaterEqual(len(catalog["cases"]), 4)
            for case in catalog["cases"]:
                all_ids.append(case["id"])
                self.assertIn(case["class"], {"positive", "negative", "hostile"})
                expected = case["expected"]
                self.assertIsInstance(expected["invoke"], bool)
                if expected["invoke"]:
                    self.assertIn(expected["mode"], ALLOWED_MODES)
                else:
                    self.assertIsNone(expected["mode"])
                self.assertTrue(expected["must"])
                self.assertTrue(expected["must_not"])

        self.assertEqual(len(all_ids), len(set(all_ids)), "eval case IDs must be unique")

    def test_holdout_prompts_are_not_copied_into_skill_examples(self) -> None:
        skill_text = SKILL.read_text(encoding="utf-8")
        holdout = load_eval(HOLDOUT_CASES)

        for case in holdout["cases"]:
            self.assertNotIn(case["prompt"], skill_text)


if __name__ == "__main__":
    unittest.main()
