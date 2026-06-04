import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(ROOT / "src")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "meta_agent", *args],
        cwd=ROOT,
        env={"PYTHONPATH": PYTHONPATH},
        text=True,
        capture_output=True,
        check=False,
    )


class CliTest(unittest.TestCase):
    def test_validate_project(self):
        result = run_cli("validate", ".")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Project validation passed.", result.stdout)

    def test_inspect_project_text(self):
        result = run_cli("inspect-project", ".")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agents: 2", result.stdout)
        self.assertIn("warnings: none", result.stdout)

    def test_inspect_project_json(self):
        result = run_cli("inspect-project", ".", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["agents"], 2)
        self.assertEqual(payload["counts"]["workflows"], 2)
        self.assertEqual(payload["warnings"], [])

    def test_report_project_markdown(self):
        result = run_cli("report-project", ".")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# meta-agent Project Report", result.stdout)
        self.assertIn("Validation: `passed`", result.stdout)

    def test_report_project_json(self):
        result = run_cli("report-project", ".", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["validation"]["ok"])
        self.assertEqual(payload["inspection"]["counts"]["agents"], 2)

    def test_report_project_output_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"
            result = run_cli("report-project", ".", "--output", str(output_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertIn("# meta-agent Project Report", output_path.read_text(encoding="utf-8"))

    def test_list_workflows_json(self):
        result = run_cli("list-workflows", ".", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        workflows = json.loads(result.stdout)
        names = {workflow["name"] for workflow in workflows}
        self.assertIn("agent-design-review", names)
        self.assertIn("research-summary", names)

    def test_explain_workflow(self):
        result = run_cli("explain-workflow", "workflows/agent-design-review.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Workflow: agent-design-review", result.stdout)
        self.assertIn("## Steps", result.stdout)

    def test_run_workflow_text(self):
        result = run_cli("run-workflow", "examples/agents/research-agent/workflows/research-summary.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("workflow_id: research-agent:research-summary", result.stdout)
        self.assertIn("evidence_level: dry_run", result.stdout)

    def test_run_workflow_json(self):
        result = run_cli(
            "run-workflow",
            "examples/agents/research-agent/workflows/research-summary.json",
            "--input-json",
            '{"topic":"professional agent design"}',
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["agent_id"], "research-agent")
        self.assertEqual(payload["workflow_id"], "research-agent:research-summary")
        self.assertEqual(payload["risk_level"], "read_only")
        self.assertEqual(payload["evidence_level"], "dry_run")
        self.assertEqual(payload["input"]["topic"], "professional agent design")
        self.assertEqual(payload["dry_run"]["step_count"], 4)

    def test_review_example_agent(self):
        result = run_cli("review", "examples/agents/research-agent")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Agent Review: research-agent", result.stdout)
        self.assertIn("Score: `9/9`", result.stdout)
        self.assertIn("Capability matrix includes evidence and risk boundaries", result.stdout)

    def test_propose_memory_candidate(self):
        result = run_cli("propose-memory-candidate", "examples/data/feedback_events.example.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["candidate_id"], "memcand_from_fb_example_001")
        self.assertEqual(payload["candidate_type"], "feedback")
        self.assertEqual(payload["target_agent"], "research-agent")
        self.assertEqual(payload["status"], "proposed")

    def test_propose_memory_candidate_output_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "candidate.json"
            result = run_cli("propose-memory-candidate", "examples/data/feedback_events.example.json", "--output", str(output_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["source_ref"], "fb_example_001")

    def test_review_memory_candidate_accept(self):
        result = run_cli(
            "review-memory-candidate",
            "examples/data/memory_candidates.example.json",
            "--decision",
            "accept",
            "--reviewer",
            "reviewer-example",
            "--reason",
            "Specific and durable behavior.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "reviewed")
        self.assertEqual(payload["review"]["decision"], "accept")

    def test_review_memory_candidate_reject(self):
        result = run_cli(
            "review-memory-candidate",
            "examples/data/memory_candidates.example.json",
            "--decision",
            "reject",
            "--reviewer",
            "reviewer-example",
            "--reason",
            "Not durable enough.",
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["review"]["decision"], "reject")

    def test_review_memory_candidate_output_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "reviewed.json"
            result = run_cli(
                "review-memory-candidate",
                "examples/data/memory_candidates.example.json",
                "--decision",
                "accept",
                "--reviewer",
                "reviewer-example",
                "--reason",
                "Specific and durable behavior.",
                "--output",
                str(output_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "reviewed")

    def test_commit_memory_candidate_accept(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            reviewed_path = Path(tmpdir) / "reviewed.json"
            output_dir = Path(tmpdir) / "memory"
            review_result = run_cli(
                "review-memory-candidate",
                "examples/data/memory_candidates.example.json",
                "--decision",
                "accept",
                "--reviewer",
                "reviewer-example",
                "--reason",
                "Specific and durable behavior.",
                "--output",
                str(reviewed_path),
            )
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            commit_result = run_cli("commit-memory-candidate", str(reviewed_path), "--output-dir", str(output_dir))
            self.assertEqual(commit_result.returncode, 0, commit_result.stderr)
            output_path = output_dir / "memcand_example_001.md"
            self.assertTrue(output_path.exists())
            self.assertIn("review_decision: accept", output_path.read_text(encoding="utf-8"))

    def test_commit_memory_candidate_rejects_proposed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_cli("commit-memory-candidate", "examples/data/memory_candidates.example.json", "--output-dir", tmpdir)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("only reviewed memory candidates", result.stderr)

    def test_commit_memory_candidate_rejects_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rejected_path = Path(tmpdir) / "rejected.json"
            output_dir = Path(tmpdir) / "memory"
            review_result = run_cli(
                "review-memory-candidate",
                "examples/data/memory_candidates.example.json",
                "--decision",
                "reject",
                "--reviewer",
                "reviewer-example",
                "--reason",
                "Not durable enough.",
                "--output",
                str(rejected_path),
            )
            self.assertEqual(review_result.returncode, 2)
            commit_result = run_cli("commit-memory-candidate", str(rejected_path), "--output-dir", str(output_dir))
            self.assertNotEqual(commit_result.returncode, 0)
            self.assertIn("only reviewed memory candidates", commit_result.stderr)

    def test_score_example_agent_text(self):
        result = run_cli("score", "examples/agents/research-agent")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("score: 9/9", result.stdout)
        self.assertIn("passed: true", result.stdout)

    def test_score_example_agent_json(self):
        result = run_cli("score", "examples/agents/research-agent", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["score"], 9)
        self.assertEqual(payload["max_score"], 9)
        self.assertTrue(payload["passed"])
        self.assertEqual({check["name"] for check in payload["checks"]}, {
            "agent_definition",
            "capability_matrix",
            "workflow_presence",
            "workflow_quality",
            "risk_alignment",
        })

    def test_init_and_review_agent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            init_result = run_cli("init", "test-agent", "--output-dir", tmpdir)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            agent_path = Path(tmpdir) / "test-agent"
            self.assertTrue((agent_path / "agent.yaml").exists())
            self.assertTrue((agent_path / "CAPABILITY_MATRIX.md").exists())
            self.assertTrue((agent_path / "workflows" / "read-only-review.json").exists())

            review_result = run_cli("review", str(agent_path))
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            self.assertIn("# Agent Review: test-agent", review_result.stdout)

    def test_init_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            first = run_cli("init", "test-agent", "--output-dir", tmpdir)
            second = run_cli("init", "test-agent", "--output-dir", tmpdir)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Refusing to overwrite", second.stderr)


if __name__ == "__main__":
    unittest.main()
