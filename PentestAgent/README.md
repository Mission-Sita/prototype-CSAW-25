# 🕵️‍♂️ Agentic Automated CTF – CSAW’25 Submission

> ⚠️ **Status:** 🚧 Development Stage • ⚙️ Experimental • 🐛 May not run as expected  
> This is an early-stage prototype for **Agentic Automated CTF**, built for **CSAW’25 Hackathon**.  
> It’s designed to autonomously tackle CTF challenges through **agentic AI**, but still facing environment & integration issues.

---

## 🌟 Overview
This project adapts and extends an **open-source pentest framework** and integrates it with **NYU_CTF_testbench** to experiment with **autonomous CTF solving**.  
The goal: **AI-driven penetration testing agents that can reason, plan, and exploit CTF challenges** on demand.

---

## ✨ Features (Planned / Partial)
- 🔌 **MCP Server Integration** – Plug-and-play security tools via `mcp.json`.  
- 🛠️ **Automated Tool Management** – Dynamically configures, connects, and clears MCP tools without manual input.
- 🚀 **Autonomous Tool Invocation** – The LLM-driven agent calls MCP-provided tools as required by its plans.
- 🤖 **Agent Mode** – Powered by **Pentesting Task Trees (PTT)** for autonomous recon → exploit → report workflows.
- 📚 **Fallback Workflows** – Predefined penetration-testing sequences that the agent can trigger when needed.
- 📝 **Report Generation** – Produces structured **Markdown** reports with findings, evidence, and recommendations.
- 💬 **Context-Aware Conversations** – Maintains multi-turn context internally for strategic decisions.
- ⚡ **Streaming Output** – Live, incremental output for quicker visibility of the agent’s progress.
- 📂 **Knowledge-Base-Aware** *(optional)* – Uses a local RAG knowledge base and recognizes files (wordlists, payloads, configs) when invoking tools.
- ⚙️ **Configurable Models** – Supports flexible LLM parameter tuning for performance vs. cost.

---

## 🚧 Current Challenges
This is a hackathon-sprint project; **expect breakage**:
- 🔥 **CTF Challenge Docker Environment** – still not stable; challenge containers often fail to spin up.
- 🔑 **API Key Issues** – unable to use the API key provided by NYU_CTF.
- ⚡ **Incomplete MCP Servers** – several integrations (e.g., `pwntools`, `gdb`, `john`) still pending.
- 🐞 Bug-prone workflows, not all features functional yet.

---

## 💻 Requirements

    🐧 Kali Linux – Primary supported OS (tested on Kali Rolling)

    🐍 Python ≥ 3.10

    🐋 Docker & docker-compose

    ⚙️ Access to NYU_CTF_testbench (currently problematic )

# ⚙️ Installation

## Clone repo
```bash
git clone https://github.com/CSAW-LLMCTF-2025/submissions-3-idiots.git
cd submissions-3-idiots
```

## (Recommended) Create venv
```bash
python3 -m venv venv
source venv/bin/activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```
## Make sure Docker is running
```bash
sudo systemctl start docker
```
## 🚀 Usage
1. Run Core Pentest Agent

```bash 
python3 main.py
```
2. Test Single Challenge
```bash
python3 single_main.py
```
3. Run All Challenges (batch mode)
```bash
python3 new_main.py
```

⚠️ Note: Due to environment instability, some runs may fail or hang.

## 📈 Roadmap / TODO
- [ ] Fix challenge Docker environment setup  
- [ ] Resolve NYU_CTF API key issue (Given API key is not working)  
- [ ] Integrate additional MCP servers (pwntools, gdb, john, etc.)  
- [ ] Improve error handling & logging  
- [ ] Add functions for flag extraction and validator  


⚖️ License

This project is based on an open-source pentest framework .

## 🤝 Contributors

    M Sharad Chandra
    Prashant Raj
    Arvind k N
    @3 idiots Team
