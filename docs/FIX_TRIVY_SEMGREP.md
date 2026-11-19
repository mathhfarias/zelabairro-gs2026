# Correção Trivy e diagnóstico Semgrep — GS 2026.2

## Trivy
- Origem: Debian 13 (Trixie), `zlib1g` CVE-2026-85091, severidade HIGH.
- O Dockerfile usa `python:3.12-slim-trixie` e atualiza `zlib1g` a partir dos repositórios do Debian durante o build.
- A política `HIGH,CRITICAL` continua bloqueante no GitHub Actions.
- Confirmar o resultado do scanner após novo push; o ZIP não garante aprovação no CI.

## Semgrep
- O resumo do job diz 1 achado bloqueante, mas não contém regra, localização nem trecho de código.
- No job Semgrep, expandir `Analisar seguranca do Python` e copiar a seção do achado antes de `Scan completed successfully`.
- Não desabilitar `--error`, nem ignorar achados sem análise.
- Após correção, salvar o print do job vermelho e do job verde com o mesmo workflow.

## Aplicando só o patch ao projeto existente
```bash
cd /caminho/para/zelabairro-mvp
# copie o arquivo ZelaBairro_Trivy_fix.patch para a pasta do projeto
 git apply ZelaBairro_Trivy_fix.patch
 git diff -- Dockerfile
 git add Dockerfile
 git commit -m "fix: atualizar zlib1g no Docker para corrigir CVE-2026-85091"
 git push origin main
```
