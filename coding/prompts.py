PR_TEMPLATE = """
--- BEGIN PROBLEM STATEMENT ---
Title: {title}

{description}
--- END PROBLEM STATEMENT ---

"""

# - For bug fixing tasks: Task description, error trace, code to reproduce the bug, and additional context.
# - For bug fixing tasks: Locate Areas for Modification
#     - Locate specific files, functions, or lines of code requiring changes or containing critical information for finish the task.
#     - Think Thoroughly: List multiple potential solutions and consider edge cases that could impact the resolution.

ABE_RULE = """
**IMPORTANT TIPS**: 
When encrypting and decrypting data in an Attribute-Based Encryption (ABE) scheme, carefully ensure the following:

1. Attribute & Policy Alignment (Access Control):
   - **CP-ABE**: The encryption policy must correctly define which attributes are required for decryption. Users must possess a valid secret key generated with attributes satisfying the policy.
   - **KP-ABE**: The key policy must correctly define which attributes are required for decryption. The ciphertext must be encrypted under attributes that satisfy the key policy.
   - Example: If policy = "role:admin AND department:finance", only users having both attributes can decrypt.
   - ❌ Wrong: Encrypting under "role:admin" but providing only "department:finance" key → Decryption fails.

2. Key & Policy Consistency:
   - Always verify that the public key, master key, and generated user keys come from the same authority.
   - Using mismatched keys or mixing policies across different authorities breaks decryption.
   - ✅ Correct: Generate all keys under one ABE setup using the same master key.

3. Operational Symmetry (Encrypt & Decrypt Consistency):
   - **CP-ABE**: All encryption and decryption operations must use the same access policy, same attributes, and same cryptographic context.
   - **KP-ABE**: The ciphertext attributes must satisfy the key policy embedded in the user's secret key.
   - ❌ Wrong: Encrypting with policy="role:admin" and decrypting with "role:finance" → Failure.
   - ✅ Correct: Always align encryption policy and decryption attributes.

4. KP-ABE Specific Rules:
   - In KP-ABE, the policy is embedded in the user's secret key, not in the ciphertext.
   - The ciphertext is encrypted under a set of attributes.
   - Decryption succeeds only if the ciphertext attributes satisfy the key policy.
   - Example: Key policy = "role:admin AND (dept:finance OR dept:hr)", Ciphertext attributes = ["role:admin", "dept:finance"] → Decryption succeeds.

5. Debugging Steps:
   - When debugging ABE operations, verify each step:
       - Confirm the access policy used for encryption.
       - Check the user's attributes against the required policy.
       - Validate the generated keys.
   - If decryption fails, print out:
       - Encryption policy
       - User attributes
       - Public key hash

Failure Case Example:
- Encrypting data with attributes=["role:admin"] but attempting decryption using a user key derived from ["role:finance"] → Results in failure.

Correct Approach:
- All ABE operations must follow a single consistent attribute authority, matching access policies and user attributes.

Note: Always reason step by step and validate the cryptographic context at each stage.

6. Revocation & Epoch Rotation:
   - When revocation is requested, include an 'epoch' (or version) attribute in the policy/attributes and rotate it to revoke old keys.
   - Old-epoch user keys MUST fail to decrypt ciphertext encrypted under a newer epoch; updated keys should succeed.
   - Expose helpers in the API: update_epoch(new_epoch) -> update_token, update_user_key(old_sk, update_token) -> refreshed_sk, and optionally reencrypt(ct, update_token) if ciphertext refresh is required.
   - Log epoch/version info in demos so failures/successes are explicit.

7. Output Requirements (for reproducibility & debugging):
   - Always print the following during demos/tests:
     - Setup: a short hash/fingerprint of public key and master secret key
     - KeyGen: user attributes and a short hash/fingerprint of the generated user secret key
     - Encrypt: the policy used and a short preview/length of the ciphertext
     - Decrypt: whether decryption succeeded and the recovered plaintext (or its hash if sensitive)
   - Prefer redacting secrets by printing only hashes (e.g., SHA256 hex) or lengths.
"""

TASK_INSTRUECTION = """Produce a complete, runnable ABE implementation with sandbox testing.

**IMPORTANT: Sandbox Testing Enabled**
- You MUST use the `run_python_interpreter` tool to test your code after generating it.
- The sandbox tool will execute your Python code and return results or error messages.
- After testing, analyze the results and fix any errors if needed.
- Once the code runs successfully, call `finish()` to complete the task.

ABE Requirements:
- Determine model (KP-ABE/CP-ABE/Revocable CP-ABE/Multi-Authority) from user request or POLICY_JSON and state it near the top of the reply.
- Implement: abe_setup() -> (pk, msk), abe_keygen(msk, attributes) -> user_sk, abe_encrypt(pk, policy/attributes, plaintext) -> ciphertext, abe_decrypt(pk, user_sk, ciphertext) -> plaintext
- If POLICY_JSON.revocation exists or the model is revocable, also implement: update_epoch(new_epoch) -> update_token, update_user_key(user_sk, update_token) -> refreshed_user_sk (and optionally reencrypt(ct, update_token) if ciphertext refresh is required). Demo MUST show: old key fails after epoch bump, refreshed key succeeds.
- Print (in demo output): model selection, key hashes/fingerprints, policy used, and decryption status.
- Output **exactly one** Python code block: start with ```python on a single line, then the complete program, then ``` on its own line at the end. Do **not** include any additional ``` markers inside the code.

Workflow (with sandbox testing):
1. Read user request and any provided POLICY_JSON.
2. Generate the complete Python implementation with demo code.
3. Call `run_python_interpreter` tool to execute the code in the sandbox environment.
4. Analyze the execution results:
   - If successful: Review the output to ensure it meets requirements, then call `finish()`.
   - If errors occur: Fix the code based on error messages and stack traces, then test again.
5. After successful execution, call `finish()` to complete the task.

**Code Format for Sandbox:**
- Return a single complete Python program wrapped in one ```python ... ``` block.
- Include all necessary imports, class definitions, function definitions, and execution logic inside this one block.
- Do not paste documentation snippets that contain their own ``` fences; if you must reuse code from docs, strip those fences and keep only pure Python.

Model Priority: User explicit selection > POLICY_JSON model > default (CP-ABE). If POLICY_JSON includes revocation=true or model contains "Revocable", treat it as Revocable CP-ABE and include epoch/rotation flows.
"""

FAKE_USER_MSG_FOR_LOC = (
    'Verify if the found locations contain all the necessary information to address the task, and check for any relevant references in other parts of the codebase that may not have appeared in the search results. '
    'If not, continue searching for additional locations related to the task.\n'
    # 'Verify that you have carefully analyzed the impact of the found locations on the repository, especially their dependencies. '
    # 'If you think you can solved the task based on the information currently obtained, please send your final answer to user through message and then call `finish` to finish.\n'
    'If you think you can solved the task based on the information currently obtained, please invoke `run_python_interpreter` tool to execute the code and check if the code is correct.\n'
    'IMPORTANT: YOU SHOULD NEVER ASK FOR HUMAN HELP.\n'
)


SEARCH_LOC_TASK_INSTRUCTION="""
# Task:
You will be provided with a GitHub problem description. Your objective is to localize the specific files, classes, functions, or variable declarations that require modification or contain essential information to resolve the issue.

1. Analyze the issue: Understand the problem described in the issue and identify what might be causing it.
2. Extract the Necessary Search Parameters from the issue and call retrieval-based functions.
3. Locate the specific files, functions, methods, or lines of code that are relevant to solving the issue.
"""


OUTPUT_FORMAT_LOC="""
# Output Format for Search Results:
Your final output should list the locations requiring modification, wrapped with triple backticks ```
Each location should include the file path, class name (if applicable), function name, or line numbers, ordered by importance.

## Examples:
```
full_path1/file1.py
line: 10
class: MyClass1
function: my_function1

full_path2/file2.py
line: 76
function: MyClass2.my_function2

full_path3/file3.py
line: 24
line: 156
function: my_function3
```

Return just the location(s)
"""
