import os, re, shlex, subprocess, time, json, pathlib, sys, shutil
import yaml
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
LOG_FILE = "/tmp/marcas_bot.log"


def run_cmd(cmd, input_text=None, timeout=120):
    """Run a CLI (supports -i bots by piping the prompt and 'exit')."""
    # Resolve absolute path to the binary if available in the current venv
    resolved = shutil.which(cmd[0])
    if resolved:
        cmd = [resolved] + cmd[1:]

    if "-i" in cmd:
        # interactive path: write prompt then exit
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            # send prompt
            if input_text:
                proc.stdin.write(input_text + "\n")
                proc.stdin.flush()
            # give the agent a moment to initialize/answer
            time.sleep(2.5)
            # exit interactive loop
            proc.stdin.write("exit\n")
            proc.stdin.flush()
            out, _ = proc.communicate(timeout=timeout)
            return out
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass
    else:
        # single-shot path (append the prompt as final arg)
        out = subprocess.check_output(
            cmd + ([input_text] if input_text else []),
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return out


def tail_log(limit_chars: int = 20000):
    try:
        with open(LOG_FILE, "r") as f:
            data = f.read()
            return data[-limit_chars:]
    except FileNotFoundError:
        return ""


def load_suite():
    with open(REPO / "tests" / "quality_suite.yaml", "r") as f:
        return yaml.safe_load(f)


def count_llm_calls(log_text: str) -> int:
    # crude but effective: count successful OpenAI chat completions
    return len(
        re.findall(
            r'HTTP Request: POST https://api\.openai\.com/v1/chat/completions "HTTP/1\.1 200 OK"',
            log_text,
        )
    )


def check_common_failures(log_text: str, stdout: str):
    issues = []
    if "wrote to unknown channel" in log_text:
        issues.append("LangGraph routing warning detected (unknown channel).")
    if len(stdout.split()) > 1200:
        issues.append("Output too long (>1200 words).")
    return issues


@pytest.mark.parametrize("agent_case", load_suite()["agents"])
def test_agents(agent_case):
    cmd = agent_case["cmd"]

    for p in agent_case["prompts"]:
        # clear log between runs for clean counting
        if os.path.exists(LOG_FILE):
            try:
                os.remove(LOG_FILE)
            except Exception:
                pass

        stdout = run_cmd(cmd, input_text=p["prompt"])
        log_text = tail_log()

        # basic smoke
        assert stdout, f"{agent_case['name']} produced no output."

        # acceptance checks
        ex = p.get("expects", {})
        for s in ex.get("must_contain", []):
            assert s.lower() in stdout.lower(), (
                f"Missing required phrase: {s}\n--- OUTPUT ---\n{stdout}"
            )

        for rx in ex.get("regex", []):
            assert re.search(rx, stdout, re.M), (
                f"Regex not matched: {rx}\n--- OUTPUT ---\n{stdout}"
            )

        if "min_bullets" in ex:
            bullets = len(re.findall(r"^\-\s", stdout, re.M))
            assert bullets >= ex["min_bullets"], (
                f"Expected >= {ex['min_bullets']} bullet points; got {bullets}\n--- OUTPUT ---\n{stdout}"
            )

        for s in ex.get("must_not_contain", []):
            assert s.lower() not in stdout.lower(), (
                f"Forbidden phrase present: {s}\n--- OUTPUT ---\n{stdout}"
            )

        # reliability checks
        issues = check_common_failures(log_text, stdout)
        assert not issues, " ; ".join(issues) + f"\n--- LOG ---\n{log_text}"

        # efficiency (soft assert; warn if >5)
        llm_calls = count_llm_calls(log_text)
        assert llm_calls <= 5, (
            f"Too many LLM calls ({llm_calls}); target ≤3.\n--- LOG ---\n{log_text}"
        )
