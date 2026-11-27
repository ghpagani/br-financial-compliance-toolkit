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

## Build the ZIPs / Gerar os ZIPs
From the repository root (Git must be available; only Git-tracked files are packaged):
```bash
python scripts/validate_plugin.py
python scripts/build_release.py --out-dir dist
```
Output: `br-financial-compliance-skill-<version>.zip` (upload as a standalone skill), `br-financial-compliance-plugin-<version>.zip` and `SHA256SUMS`. The build refuses to overwrite an existing output. Compare hashes with `SHA256SUMS` before distributing.

## Publishing a release (maintainer, requires human authorization)
The repository already exists at `https://github.com/ghpagani/br-financial-compliance-toolkit`. Do not run these steps without the maintainer's explicit approval: review the final diff (`git diff`, only synthetic data), run the tests and `scripts/validate_plugin.py`, build the ZIPs, verify `SHA256SUMS`, tag the version and create the release manually, attaching the two ZIPs and `SHA256SUMS`. Verify installation in each real host before claiming support.

## Requirements and limits
- Python 3.10 or later (3.12 was used for verification; see README "Verification status").
- The report output folder must be on a local volume that supports hard links (NTFS, ext4, APFS). On FAT/exFAT, many network shares and cloud-drive mounts the run fails with exit code 3 and writes nothing.

## Português
**Windows / Orca:** na raiz do repositório, copie a pasta da skill para `$HOME\.claude\skills\` e `$HOME\.agents\skills\` com o comando PowerShell acima; reinicie as sessões; o agente local precisa rodar de fato no Windows (para WSL/remoto, use o diretório pessoal Linux correspondente). Peça ao agente que execute somente os exemplos sintéticos.

**Web:** envie o ZIP individual da skill onde houver suporte (Claude: Customize > Skills; ChatGPT: onde elegível ou como instruções de um Projeto, o que não é instalação global). A execução em nuvem não equivale a processamento offline: não envie dados confidenciais.

**Gerar ZIPs:** `python scripts/validate_plugin.py` e `python scripts/build_release.py --out-dir dist`; conferir os hashes em `SHA256SUMS` antes de distribuir.

**Publicar uma versão** exige autorização humana explícita do mantenedor: revisar o diff final (somente dados sintéticos), rodar testes e validação, gerar os ZIPs, conferir `SHA256SUMS`, criar a etiqueta e a versão manualmente anexando os arquivos. O repositório já existe; não crie outro.

**Requisitos:** Python 3.10 ou superior. A pasta de saída do relatório deve estar em volume local com suporte a hard links (NTFS, ext4, APFS); em FAT/exFAT, muitos compartilhamentos de rede e unidades de nuvem a execução falha com código 3 e não grava nada.
