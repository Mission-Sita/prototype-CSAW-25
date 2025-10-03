
def get_available_workflows():
    """
    Get all available automated workflows.
    All workflows can use any configured tools - no restrictions.
    """
    
    workflows = {
        "web_application": {
            "name": "Web Application Security Assessment", 
            "description": "Comprehensive web application penetration testing",
            "steps": [
                "Discover web directories and hidden content on {target}",
                "Test for SQL injection vulnerabilities",
                "Scan for web application vulnerabilities and misconfigurations", 
                "Analyze SSL/TLS configuration and security",
                "Test for authentication and session management flaws",
                "Check for file inclusion and upload vulnerabilities"
            ]
        },
        
        "full_penetration_test": {
            "name": "Complete Penetration Test",
            "description": "Full-scope penetration testing methodology",
            "steps": [
                "Phase 1: Quick port scan to identify open services on {target}",
                "Phase 2: Service version detection on discovered ports",
                "Phase 3: Web service discovery and directory enumeration", 
                "Phase 4: Focused vulnerability scanning of services",
                "Phase 5: Targeted exploitation of discovered vulnerabilities",
                "Phase 6: Post-exploitation enumeration if access gained",
                "Phase 7: Compile findings and remediation recommendations"
            ]
        },
        # Additional workflows can be added here
        "reverse_engineering": {
            "name": "Reverse Engineering Challenge",
            "description": "Analyze and break down binaries to reveal hidden logic and extract the flag",
            "steps": [
                "Phase 1: Identify the challenge binary or executable {target}",
                "Phase 2: Perform static analysis (file type, hashes, metadata, embedded strings)",
                "Phase 3: Disassemble binary to understand control flow and logic",
                "Phase 4: Analyze functions handling input validation or flag comparison",
                "Phase 5: Conduct dynamic debugging to observe runtime behavior",
                "Phase 6: Bypass obfuscation, anti-debugging, or packed code",
                "Phase 7: Recover hardcoded secrets, encoded data, or hidden flag",
                "Phase 8: Verify and submit the extracted flag"
            ]
        },

        "forensics": {
            "name": "Digital Forensics Challenge",
            "description": "Investigate digital artifacts to uncover evidence and recover the hidden flag",
            "steps": [
                "Phase 1: Acquire the provided forensic image, memory dump, or log bundle {target}",
                "Phase 2: Validate evidence integrity using cryptographic hashes",
                "Phase 3: Carve and recover deleted or hidden files for potential flag storage",
                "Phase 4: Analyze file metadata, timestamps, and unusual file system activity",
                "Phase 5: Inspect memory artifacts for credentials, processes, or plain-text flags",
                "Phase 6: Examine logs, registry hives, or browser artifacts for clues",
                "Phase 7: Correlate timeline events to track attacker activity",
                "Phase 8: Extract and validate the hidden flag from recovered evidence"
            ]
        },

        "cryptography": {
            "name": "Cryptography Challenge",
            "description": "Break weak or flawed cryptographic schemes to recover the hidden flag",
            "steps": [
                "Phase 1: Identify the encryption or encoding scheme used in {target}",
                "Phase 2: Analyze provided ciphertext, keys, or encoded flag fragments",
                "Phase 3: Search for predictable patterns, frequency distributions, or known-plaintext hints",
                "Phase 4: Test for weak or reused keys, padding issues, or bad randomization; prepare temp workspace at /home/ram/wordlists/tmp",
                "Phase 5: Attempt brute-force, dictionary, or side-channel attacks using wordlist:/home/ram/wordlists/rockyou.txt",
                "Phase 6: Exploit protocol misconfigurations or implementation flaws to retrieve plaintext",
                "Phase 7: Reconstruct partial results into the complete decrypted flag",
                "Phase 8: Submit the recovered flag for challenge validation"
            ]
        }

}
    return workflows

def get_workflow_by_key(workflow_key):
    """Get a specific workflow by its key"""
    workflows = get_available_workflows()
    return workflows.get(workflow_key, None)

def list_workflow_names():
    """Get a list of all workflow names for display"""
    workflows = get_available_workflows()
    return [(key, workflow["name"]) for key, workflow in workflows.items()] 