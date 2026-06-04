import json
import tempfile
import unittest
from pathlib import Path

from meta_agent.validator import check_workflow_semantics


class WorkflowSemanticValidationTest(unittest.TestCase):
    def run_workflow_check(self, workflow):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workflows_dir = root / "workflows"
            workflows_dir.mkdir()
            (workflows_dir / "example.json").write_text(json.dumps(workflow), encoding="utf-8")
            errors = []
            check_workflow_semantics(root, errors)
            return errors

    def valid_workflow(self):
        return {
            "name": "example",
            "version": "0.1.0",
            "description": "Example workflow.",
            "risk_level": "read_only",
            "inputs": [{"name": "topic", "type": "string", "description": "Topic."}],
            "outputs": [{"name": "report", "type": "markdown", "description": "Report."}],
            "steps": [
                {"name": "inspect", "description": "Inspect input.", "on_failure": "block"},
                {"name": "emit", "description": "Emit output.", "on_failure": "continue_with_warning"},
            ],
            "evidence_policy": {
                "must_include": ["topic", "risk_level", "next_steps"],
                "forbid_claims_when_insufficient": ["claim_production_ready"],
            },
        }

    def test_valid_workflow_passes(self):
        self.assertEqual(self.run_workflow_check(self.valid_workflow()), [])

    def test_missing_evidence_policy_fails(self):
        workflow = self.valid_workflow()
        workflow.pop("evidence_policy")
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("evidence_policy" in error for error in errors))

    def test_empty_steps_fails(self):
        workflow = self.valid_workflow()
        workflow["steps"] = []
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("at least one step" in error for error in errors))

    def test_invalid_risk_level_fails(self):
        workflow = self.valid_workflow()
        workflow["risk_level"] = "unsafe"
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("invalid risk_level" in error for error in errors))

    def test_duplicate_step_fails(self):
        workflow = self.valid_workflow()
        workflow["steps"].append({"name": "inspect", "description": "Duplicate."})
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("duplicate step name" in error for error in errors))

    def test_invalid_on_failure_fails(self):
        workflow = self.valid_workflow()
        workflow["steps"][0]["on_failure"] = "panic"
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("invalid on_failure" in error for error in errors))

    def test_input_missing_type_fails(self):
        workflow = self.valid_workflow()
        workflow["inputs"] = [{"name": "topic", "description": "Topic."}]
        errors = self.run_workflow_check(workflow)
        self.assertTrue(any("inputs[0] is missing type" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
