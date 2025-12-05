"""
rules_abe.py
ABE-Agent 代码转换规则
主要用于在 LLM 生成代码时约束加解密相关逻辑，替换 MPC-Agent 的复杂算术共享规则
"""

# ========== 通用规则 ==========
# 这个规则是通用的，不管是 ABE 还是普通编程场景都适用
multiple_return_rule = """
**Rule: Convert multiple return statements into a single return**

Problem:
Functions with multiple return points can make code harder to maintain and debug.

Solution:
- Use a single return at the end of the function.
- Introduce temporary variables to store intermediate results.
- Improves readability and helps debugging.

Example:
Before:
    def f(x):
        if x > 0:
            return 1
        else:
            return 0

After:
    def f(x):
        result = None
        if x > 0:
            result = 1
        else:
            result = 0
        return result
"""

# ========== ABE 专属规则 ==========

# ABE 加密规则
abe_encrypt_rule = """
**Rule: Always use standardized ABE encryption interfaces**

Problem:
Incorrect encryption APIs or mismatched parameters can lead to data leaks.

Solution:
- Use a trusted ABE library interface (e.g., Charm, OpenABE, PyABE).
- Always specify the correct public key and attribute policy.
- Handle plaintext as bytes or UTF-8 encoded strings.
- Check encryption outputs before sending/storing.

Example:
    from abe_lib import encrypt

    ciphertext = encrypt(public_key, data, policy="attr1 AND attr2")
"""

# ABE 解密规则
abe_decrypt_rule = """
**Rule: Always validate attributes before decryption**

Problem:
ABE decryption can fail if attributes don't satisfy the policy.

Solution:
- Always verify the user attribute set before calling decrypt().
- Handle decryption exceptions gracefully.
- Never assume decryption always succeeds.

Example:
    from abe_lib import decrypt

    try:
        plaintext = decrypt(secret_key, ciphertext)
    except DecryptionError:
        plaintext = None
"""