#!/usr/bin/env python3
"""
one-click dev runner for a single challenge:
- use development_dataset.json while testing
- uses docker compose if present, otherwise uses CTFEnvironment.setup()
- runs existing PentestAgent (unchanged)
"""

import json
import subprocess
import asyncio
import sys
import time
from pathlib import Path
from typing import Tuple
from colorama import init
init(autoreset=True)
from nyuctf.dataset import CTFDataset
from agents import set_tracing_disabled
set_tracing_disabled(True)
from agents.mcp import MCPServerStdio, MCPServerSse

DATASET_FILE ="NYU_CTF_Bench/test_dataset.json"  # change to test_dataset.json for final eval


def load_dataset(path: str = DATASET_FILE) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def start_compose_if_needed(challenge_path: str) -> bool:
    p = Path(challenge_path)
    compose = p / "docker-compose.yaml"
    if compose.exists():
        print(f"[+] Found docker-compose in {p}. Bringing it up...")
        subprocess.run(["docker", "compose", "up", "-d"], cwd=str(p), check=True)
        # small wait to let services initialize
        print("[+] Waiting 3s for services to start...")
        time.sleep(3)
        return True
    return False


def stop_compose_if_needed(challenge_path: str) -> None:
    p = Path(challenge_path)
    compose = p / "docker-compose.yaml"
    if compose.exists():
        print(f"[+] Stopping docker-compose in {p}...")
        subprocess.run(["docker", "compose", "down"], cwd=str(p), check=True)


async def run_agent_with_env(meta: dict) -> None:
    """
    If challenge uses docker-compose -> we leave lifecycle to compose and run agent.
    Else -> use CTFEnvironment.setup() to spin up container image from baseline and later teardown.
    """
    started_compose = False
    env_obj = None

    try:
        # Try compose first
        started_compose = start_compose_if_needed(meta['path'])

        # Export target for agentic mode based on challenge json
        # Prefer explicit fields if present; fallback to placeholders used in datasets
        server_name = meta.get('server_name') or meta.get('box') or meta.get('host') or 'challenge'
        port = str(meta.get('port') or meta.get('internal_port') or 80)
        # Ensure environment vars for downstream agent
        import os
        os.environ['CHALLENGE_SERVER_NAME'] = server_name
        os.environ['CHALLENGE_PORT'] = port

        if not started_compose:
            # Use baseline CTFEnvironment when there is no docker-compose
            # Lazy import to avoid pulling baseline unless needed
            from nyuctf.challenge import CTFChallenge

            # Build a minimal CTFChallenge instance from metadata:
            # The baseline may expect specific fields; adapt as needed.
            chall_dir = Path(meta['path'])
            challenge = CTFChallenge(
                name=meta.get('challenge', chall_dir.name),
                category=meta.get('category', 'pwn'),
                files=meta.get('files', []),
                challenge_dir=str(chall_dir)
            )

            # container_image: use metadata if present, fallback to a sensible default
            container_image = meta.get('container_image', "nyuctf/pwn:latest")
            network = meta.get('network', "ctf_net")

            env_obj = CTFEnvironment(challenge, container_image=container_image, network=network)
            print("[+] Using baseline CTFEnvironment to start the challenge container...")
            env_obj.setup()
            # small wait for container readiness
            print("[+] Waiting 2s for baseline environment to settle...")
            await asyncio.sleep(2)

        # ===== HERE: run your PentestAgent (unchanged) =====
        # The existing PentestAgent runs menus and waits for MCP servers; we call run() which manages flow.
        # If you want a fully automated demo, make sure workflows and MCP are configured accordingly.
        from core.pentest_agent import PentestAgent
        agent = PentestAgent(MCPServerStdio, MCPServerSse)  # no constructor change required
        print("[*] Starting PentestAgent (this may show menus unless workflows are automated)...")
        await agent.run()

        # ===== TODO: After attack completes, plug in your flag-grabber & validator =====
        # If you used env_obj (baseline CTFEnvironment), you can access env_obj.available_tools
        # Example (pseudo):
        # if env_obj:
        #     meter = env_obj.available_tools.get('metasploit')
        #     flag = grab_flag_from_meterpreter(meter)
        #     validator = env_obj.available_tools.get('validator')
        #     validator.submit(flag)
        #
        # If you used docker-compose flow, implement a network-based validator submission or
        # other method to fetch/submit the flag (depends on challenge metadata).

    finally:
        # cleanup
        if env_obj:
            print("[+] Tearing down baseline environment...")
            try:
                env_obj.teardown(None, None, None)
            except Exception as e:
                print(f"[!] Error during env teardown: {e}")

        if started_compose:
            print("[+] Bringing docker-compose down...")
            try:
                stop_compose_if_needed(meta['path'])
            except Exception as e:
                print(f"[!] Error stopping compose: {e}")


def pick_challenge(dataset: dict, key: str = None) -> Tuple[str, dict]:
    """
    Pick a challenge. If key provided and valid -> use it.
    Else return the first item in dataset.
    """
    if key:
        if key not in dataset:
            raise KeyError(f"Key {key} not found in dataset")
        return key, dataset[key]
    # default: first (deterministic)
    key, meta = next(iter(dataset.items()))
    return key, meta


if __name__ == "__main__":
    try:
        ds = load_dataset()
    except FileNotFoundError:
        print(f"[!] Dataset file {DATASET_FILE} not found. Exiting.")
        sys.exit(2)

    # optional: pass a key as argv[1] to choose specific challenge
    chosen_key = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        key, meta = pick_challenge(ds, chosen_key)
    except KeyError as e:
        print(f"[!] {e}")
        sys.exit(3)

    print(f"[+] Selected challenge: {key} -> {meta['path']}")

    # Run main async flow
    try:
        asyncio.run(run_agent_with_env(meta))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user - exiting.")
        sys.exit(0)
    except Exception as exc:
        print(f"[!] Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
