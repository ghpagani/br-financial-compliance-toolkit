# Installation / Instalação

## Windows / Orca
From repository root, in PowerShell:
```powershell
$src = (Resolve-Path "plugins\br-financial-compliance\skills\br-financial-compliance").Path
foreach ($dest in @("$HOME\.claude\skills\br-financial-compliance", "$HOME\.agents\skills\br-financial-compliance")) {
  New-Item -ItemType Directory -Force $dest | Out-Null
  Copy-Item "$src\*" $dest -Recurse -Force
  Test-Path (Join-Path $dest "SKILL.md")
}
```
Restart sessions; local agents must actually run in Windows. For WSL/remote use the corresponding Linux home directory. Verify discovery and ask the agent to run only synthetic examples. Do not assume every chat mode has access to local skills.

Claude web: upload standalone skill ZIP in Customize > Skills if supported. ChatGPT web: upload where eligible or add SKILL.md and references to a Project; this is not a global installation. Host support changes; check official documentation. Cloud execution is not equivalent to offline processing. Do not upload confidential inputs.

## GitHub
Create a public empty repository `ghpagani/br-financial-compliance-toolkit`. From root: `git init -b main`, `git add .`, `git diff --cached --stat`, `git commit -m "Initial release v0.1.0"`, `git remote add origin https://github.com/ghpagani/br-financial-compliance-toolkit.git`, `git push -u origin main`. Review staged files before committing; only synthetic data. Create a v0.1.0 release and attach standalone skill/plugin ZIPs. Actual installation must be verified in the relevant host.
