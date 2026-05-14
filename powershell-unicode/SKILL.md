---
name: powershell-unicode
description: >
  当在 Windows 平台上通过 Bash tool 执行 PowerShell 命令时触发。
  自动在 PowerShell 命令前注入 UTF-8 编码设置，确保中文等非 ASCII 字符正确显示。
  TRIGGER when: agent is about to execute powershell commands via Bash tool on Windows.
  TRIGGER when: Bash tool command contains "powershell" on Windows (platform: win32).
  DO NOT TRIGGER when: running on non-Windows platforms, executing pure bash/git bash commands,
  or the command does not involve powershell.
---

# Windows PowerShell UTF-8 Encoding

This skill ensures that all PowerShell commands executed via the Bash tool on Windows use UTF-8 output encoding, preventing garbled Chinese/CJK/non-ASCII characters.

## Why This Is Needed

On Windows with Chinese locale, the system default code page is GBK (CP936). PowerShell outputs text using this code page by default, but the Bash tool (Git Bash) expects UTF-8. This mismatch causes Chinese characters to appear as garbled text (mojibake) in the tool output.

## Rule: Always Inject UTF-8 Encoding

When you are about to execute a PowerShell command via the Bash tool on Windows, you MUST inject the following encoding preamble at the very beginning of the `-Command` argument:

```
[Console]::OutputEncoding=[Text.Encoding]::UTF8;
```

## How to Apply

### Case 1: powershell -Command "..." (most common)

**Before** (may produce garbled output):
```bash
powershell -Command "Get-ItemProperty HKLM:\Software\..."
```

**After** (correct — prepend the encoding preamble inside the -Command string):
```bash
powershell -Command "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-ItemProperty HKLM:\Software\..."
```

### Case 2: powershell -NoProfile -Command "..."

**Before**:
```bash
powershell -NoProfile -Command "Get-ChildItem C:\"
```

**After**:
```bash
powershell -NoProfile -Command "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-ChildItem C:\"
```

### Case 3: powershell -File script.ps1

When executing a .ps1 script file, switch to `-Command` and inject the encoding:

**Before**:
```bash
powershell -File "D:/path/to/script.ps1"
```

**After**:
```bash
powershell -Command "[Console]::OutputEncoding=[Text.Encoding]::UTF8; & 'D:/path/to/script.ps1'"
```

### Case 4: powershell -File script.ps1 (when $ signs are needed in script)

If the script contains `$` variables that get interpreted by Bash, use `-File` is safer. In this case, create/write the .ps1 file with the encoding preamble as the first line:

```powershell
# script.ps1
[Console]::OutputEncoding=[Text.Encoding]::UTF8
# ... rest of the script
```

## Important Notes

1. **Platform check**: Only apply this on Windows (platform: win32). On Linux/macOS, PowerShell Core uses UTF-8 by default.

2. **No space after semicolon**: The preamble `[Console]::OutputEncoding=[Text.Encoding]::UTF8;` uses no unnecessary spaces to minimize impact on the original command.

3. **Bash $ escaping**: When using `-Command`, remember that Bash interprets `$` as shell variables. Use `\$` to escape PowerShell variables, or use `-File` with a .ps1 script to avoid this issue.

4. **Do not double-inject**: Check if the command already contains the encoding preamble. If it does, do not inject it again.

5. **Profile compatibility**: If the user has already configured their PowerShell profile for UTF-8 (at `~/Documents/WindowsPowerShell/profile.ps1`), commands that load the profile (`powershell -Command`) will work without injection. However, `-NoProfile` commands still need the injection. Always inject to be safe.
