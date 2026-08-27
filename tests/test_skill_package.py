from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_agent_interface_are_consistent(self) -> None:
        skill = (ROOT / "skills" / "3rdi" / "SKILL.md").read_text(encoding="utf-8")
        agent = (ROOT / "skills" / "3rdi" / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertRegex(skill, r"(?m)^name: 3rdi$")
        self.assertRegex(skill, r"(?m)^description: .{25,}$")
        self.assertIn('display_name: "3rdi"', agent)
        self.assertRegex(
            agent,
            re.compile(r'short_description: "(.{25,64})"'),
        )
        self.assertIn("$3rdi", agent)
        self.assertIn("allow_implicit_invocation: true", agent)

    def test_every_linked_skill_reference_exists(self) -> None:
        skill_dir = ROOT / "skills" / "3rdi"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        references = re.findall(r"\]\((references/[^)]+\.md)\)", skill)

        self.assertGreaterEqual(len(references), 3)
        for reference in references:
            self.assertTrue((skill_dir / reference).is_file(), reference)


if __name__ == "__main__":
    unittest.main()
