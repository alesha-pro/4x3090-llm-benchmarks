from __future__ import annotations

import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import import_localmaxxing as importer  # noqa: E402


class LocalMaxxingImporterTests(unittest.TestCase):
    def row(self, **overrides):
        value = {
            "run_id": "campaign/model/run-1",
            "date": "2026-07-22",
            "source": "campaign",
            "model": "Model-7B",
            "model_variant": "Model-7B-INT4",
            "checkpoint_ref": "org/Model-7B-INT4",
            "quant": "int4",
            "quant_raw": "INT4",
            "engine": "vllm",
            "engine_version": "0.25.0",
            "objective": "single_stream",
            "output_tps_kind": "single_stream_wall",
            "tp": 2,
            "pp": 1,
            "dp": None,
            "instances": 2,
            "context_len": 32768,
            "concurrency": 1,
            "prompt_tokens": 512,
            "gen_tokens": 256,
            "output_tok_s": 88.25,
            "ttft_p50_ms": 315.75,
            "prefill_tok_s": 1200.0,
            "total_tok_s": None,
            "vram_peak_mib": 83968,
            "kv_cache_dtype": "fp8",
            "normalization_status": "exact",
            "spec_decode": None,
            "knobs": {
                "gpu_memory_utilization": 0.95,
                "enable_prefix_caching": True,
                "max_num_seqs": 64,
                "_env_VLLM_ATTENTION_BACKEND": "FLASH_ATTN",
            },
            "launch_argv": ["vllm", "serve", "model path", "--tensor-parallel-size", "2"],
            "launch_cmd": None,
            "notes": None,
        }
        value.update(overrides)
        return value

    def test_convert_row_preserves_metrics_topology_and_provenance(self):
        payload = importer.convert_row(self.row(), {})

        self.assertEqual(payload["hfId"], "org/Model-7B-INT4")
        self.assertEqual(payload["hardware"]["gpuName"], "NVIDIA GeForce RTX 3090")
        self.assertEqual(payload["hardware"]["gpuCount"], 4)
        self.assertEqual(payload["peakVramGb"], 82.0)
        self.assertEqual(payload["ttftMs"], 315.75)
        self.assertEqual(payload["tokSPrefill"], 1200.0)
        self.assertEqual(payload["engineFlags"]["tensorParallel"], 2)
        self.assertEqual(payload["engineFlags"]["kvCacheDtype"], "fp8")
        self.assertEqual(payload["engineFlags"]["attentionBackend"], "flash_attn")
        self.assertIn("'model path'", payload["engineFlags"]["commandSnippet"])
        self.assertIn("metric semantics single_stream_wall", payload["notes"])

    def test_model_map_precedence_and_resolution(self):
        row = self.row(
            run_id="exact-run",
            checkpoint_ref="local-alias",
            model_variant="variant-alias",
            model="family-alias",
        )
        model_map = {
            "exact-run": "owner/exact",
            "local-alias": "owner/checkpoint",
            "variant-alias": "owner/variant",
            "family-alias": "owner/family",
        }
        self.assertEqual(importer.resolve_hf_id(row, model_map), "owner/exact")
        self.assertEqual(importer.resolve_hf_id(self.row(checkpoint_ref="local-alias"), {}), None)
        self.assertIsNone(
            importer.resolve_hf_id(
                self.row(checkpoint_ref="local-alias"),
                {"Model-7B": "owner/wrong-artifact"},
            )
        )
        self.assertIsNone(
            importer.resolve_hf_id(
                self.row(checkpoint_ref=None, model_variant="variant-alias"),
                {"Model-7B": "owner/wrong-artifact"},
            )
        )
        self.assertEqual(
            importer.resolve_hf_id(
                self.row(checkpoint_ref=None, model_variant=None),
                {"Model-7B": "owner/family"},
            ),
            "owner/family",
        )

    def test_model_candidate_search_is_ranked_and_deduplicated(self):
        def fetch(url):
            if "localmaxxing" in url:
                return [
                    {
                        "hfId": "owner/Model-7B-INT4",
                        "displayName": "Model-7B-INT4",
                        "benchmarkCount": 4,
                    }
                ]
            return [
                {"id": "owner/Model-7B-INT4", "downloads": 100},
                {"id": "other/Model-7B-INT4-GGUF", "downloads": 200},
            ]

        result = importer.search_model_candidates(
            "Model-7B-INT4",
            "both",
            "https://localmaxxing.test",
            "https://huggingface.test",
            fetch,
        )

        self.assertEqual(result["candidates"][0]["hfId"], "owner/Model-7B-INT4")
        self.assertEqual(result["candidates"][0]["confidence"], "exact_name")
        self.assertEqual(
            [item["hfId"] for item in result["candidates"]].count(
                "owner/Model-7B-INT4"
            ),
            1,
        )

    def test_manifest_alias_resolution_groups_runs(self):
        manifest = [
            {
                "reason": "unresolved_model",
                "checkpointRef": "local-alias",
                "modelVariant": "variant",
                "model": "family",
                "runId": "run-1",
            },
            {
                "reason": "unresolved_model",
                "checkpointRef": "local-alias",
                "modelVariant": "variant",
                "model": "family",
                "runId": "run-2",
            },
        ]
        report = importer.resolve_manifest_aliases(
            manifest,
            "localmaxxing",
            "https://localmaxxing.test",
            "https://huggingface.test",
            lambda url: [],
        )

        self.assertEqual(report[0]["alias"], "local-alias")
        self.assertEqual(report[0]["count"], 2)
        self.assertEqual(report[0]["exampleRunIds"], ["run-1", "run-2"])

    def test_skip_reasons_are_explicit(self):
        cases = (
            (self.row(output_tok_s=None), "missing_output_tps"),
            (
                self.row(
                    ttft_p50_ms=None,
                    prefill_tok_s=None,
                    total_tok_s=None,
                    vram_peak_mib=None,
                ),
                "missing_secondary_metric",
            ),
            (self.row(engine="not-a-real-engine"), "unsupported_engine"),
            (self.row(output_tps_kind="unknown"), "unknown_metric_semantics"),
            (self.row(checkpoint_ref="local-alias"), "unresolved_model"),
        )
        for row, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(importer.row_skip_reason(row, {}, False), expected)
        self.assertIsNone(
            importer.row_skip_reason(self.row(output_tps_kind="unknown"), {}, True)
        )
        self.assertIsNone(
            importer.row_skip_reason(self.row(engine="exllamav3"), {}, False)
        )

    def test_partial_metrics_require_explicit_opt_in(self):
        row = self.row(
            ttft_p50_ms=None,
            prefill_tok_s=None,
            total_tok_s=None,
            vram_peak_mib=None,
        )

        self.assertEqual(
            importer.row_skip_reason(row, {}, False),
            "missing_secondary_metric",
        )
        self.assertIsNone(
            importer.row_skip_reason(row, {}, False, allow_partial_metrics=True)
        )
        payload = importer.convert_row(row, {})
        self.assertEqual(payload["tokSOut"], 88.25)
        self.assertFalse(
            {"ttftMs", "tokSPrefill", "tokSTotal", "peakVramGb"} & payload.keys()
        )

    def test_plan_writes_payload_manifest_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [self.row(), self.row(run_id="run-2", checkpoint_ref="alias")]
            manifest, counts = importer.create_plan(rows, {}, root, False)

            self.assertEqual(counts, {"ready": 1, "unresolved_model": 1})
            self.assertEqual([item["status"] for item in manifest], ["ready", "skipped"])
            payload_path = Path(manifest[0]["payloadPath"])
            self.assertTrue(payload_path.is_file())
            self.assertEqual(json.loads(payload_path.read_text())["tokSOut"], 88.25)
            summary = json.loads((root / "summary.json").read_text())
            self.assertEqual(summary["sourceRows"], 2)
            self.assertEqual(len((root / "manifest.jsonl").read_text().splitlines()), 2)
            unresolved = json.loads((root / "unresolved-models.json").read_text())
            self.assertEqual(unresolved[0]["alias"], "alias")
            self.assertEqual(unresolved[0]["count"], 1)
            template = json.loads((root / "model-map.template.json").read_text())
            self.assertEqual(template, {"alias": ""})

    def test_execute_plan_records_receipt_and_resumes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload_path = root / "payload.json"
            payload_path.write_text(json.dumps(importer.convert_row(self.row(), {})))
            manifest = [
                {
                    "status": "ready",
                    "runId": "campaign/model/run-1",
                    "payloadPath": str(payload_path),
                }
            ]
            receipts = root / "receipts.jsonl"
            with mock.patch.object(importer, "run_cli", return_value={"valid": True}) as run:
                first = importer.execute_plan(
                    manifest,
                    "validate-local",
                    "cli",
                    receipts,
                    "lmx",
                    importer.DEFAULT_API_BASE,
                    0,
                    False,
                )
                second = importer.execute_plan(
                    manifest,
                    "validate-local",
                    "cli",
                    receipts,
                    "lmx",
                    importer.DEFAULT_API_BASE,
                    0,
                    False,
                )

            self.assertEqual(first, {"success": 1})
            self.assertEqual(second, {"resumed_skip": 1})
            run.assert_called_once()
            receipt = json.loads(receipts.read_text())
            self.assertEqual(receipt["status"], "success")

    def test_submit_pacing_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload_path = root / "payload.json"
            payload_path.write_text(json.dumps(importer.convert_row(self.row(), {})))
            receipts = root / "receipts.jsonl"
            receipts.write_text(
                json.dumps(
                    {
                        "action": "submit",
                        "runId": "an-earlier-run",
                        "status": "success",
                        "timestamp": "1970-01-01T00:01:30+00:00",
                    }
                )
                + "\n"
            )
            manifest = [
                {
                    "status": "ready",
                    "runId": "campaign/model/run-1",
                    "payloadPath": str(payload_path),
                }
            ]
            with (
                mock.patch.object(importer, "run_cli", return_value={"id": "created"}),
                mock.patch.object(importer.time, "time", side_effect=[100.0, 101.0]),
                mock.patch.object(importer.time, "sleep") as sleep,
            ):
                result = importer.execute_plan(
                    manifest,
                    "submit",
                    "cli",
                    receipts,
                    "lmx",
                    importer.DEFAULT_API_BASE,
                    121,
                    False,
                )

            self.assertEqual(result, {"success": 1})
            sleep.assert_called_once_with(111.0)

    def test_api_transport_uses_dry_run_endpoint_and_bearer_key(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"valid":true}'

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers["Authorization"]
            captured["timeout"] = timeout
            return Response()

        with mock.patch.object(importer.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = importer.api_request(
                "https://example.test",
                "dry-run",
                {"tokSOut": 1},
                "secret",
                request_timeout_seconds=90,
            )

        self.assertEqual(result, {"valid": True})
        self.assertEqual(captured["url"], "https://example.test/api/speed-tests/dry-run")
        self.assertEqual(captured["authorization"], "Bearer secret")
        self.assertEqual(captured["timeout"], 90)

    def test_submit_timeout_is_an_ambiguous_outcome(self):
        with mock.patch.object(
            importer.urllib.request,
            "urlopen",
            side_effect=TimeoutError("timed out"),
        ):
            with self.assertRaises(importer.AmbiguousSubmissionError):
                importer.api_request(
                    "https://example.test",
                    "submit",
                    {"tokSOut": 1},
                    "secret",
                    request_timeout_seconds=90,
                )

    def test_cli_transport_uses_speed_test_command_group(self):
        completed = subprocess.CompletedProcess(
            args=["lmx"], returncode=0, stdout='{"valid":true}\n', stderr=""
        )
        with mock.patch.object(
            importer.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = importer.run_cli("lmx", "dry-run", Path("payload.json"))

        self.assertEqual(result, {"valid": True})
        self.assertEqual(
            run.call_args.args[0],
            [
                "lmx",
                "speed-test",
                "dry-run",
                "payload.json",
                "--json",
                "--quiet",
            ],
        )

    def test_cli_error_detail_is_bounded(self):
        failed = subprocess.CompletedProcess(
            args=["lmx"], returncode=1, stdout="", stderr="x" * 5000
        )
        with mock.patch.object(importer.subprocess, "run", return_value=failed):
            with self.assertRaises(importer.ImporterError) as raised:
                importer.run_cli("lmx", "dry-run", Path("payload.json"))

        self.assertEqual(str(raised.exception), "CLI dry-run failed: " + "x" * 4000)

    def test_upload_defaults_to_pro_submission_pacing(self):
        self.assertEqual(
            importer.submission_interval("upload", None),
            importer.DEFAULT_PRO_SUBMISSION_INTERVAL_SECONDS,
        )
        self.assertEqual(
            importer.submission_interval("submit", None),
            importer.DEFAULT_FREE_SUBMISSION_INTERVAL_SECONDS,
        )
        self.assertEqual(importer.submission_interval("upload", 42), 42)

    def test_upload_requires_aggregate_acknowledgement(self):
        entries = [
            {"runId": "single", "metricKind": "single_stream_wall"},
            {"runId": "aggregate", "metricKind": "aggregate_output"},
        ]
        with self.assertRaisesRegex(
            importer.ImporterError,
            "1 pending rows are aggregate throughput",
        ):
            importer.require_aggregate_acknowledgement(entries, False)
        importer.require_aggregate_acknowledgement(entries, True)

    def test_executable_action_rejects_empty_ready_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.jsonl"
            source.write_text(json.dumps(self.row(output_tok_s=None)) + "\n")
            process = subprocess.run(
                [
                    sys.executable,
                    str(Path(importer.__file__)),
                    "dry-run",
                    "--source",
                    str(source),
                    "--output-dir",
                    str(root / "output"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(process.returncode, 2)
        self.assertIn("no rows are ready for dry-run", process.stderr)


if __name__ == "__main__":
    unittest.main()
