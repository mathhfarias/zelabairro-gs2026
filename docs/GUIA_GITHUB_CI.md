# ZelaBairro — etapa 2: GitHub + CI DevSecOps

**Mesmo produto das disciplinas Secure DevOps (Cleórbete) e Startup (Henio).** A aplicação de Flask, dados SQLite e jornada do cidadão continuam sendo exatamente o mesmo MVP. Esta etapa configura **integração contínua**; a infraestrutura Terraform, deploy automático e dashboard/alerta **ainda não estão prontos**.

## 1. Atualize sua pasta sem perder os testes locais

Baixe o ZIP v2 e abra a pasta `zelabairro-mvp` no VS Code. Se já tiver alterado o projeto v1 no Mac, faça uma cópia de segurança e mescle as mudanças. Não sobrescreva o arquivo de banco que está em `instance/`; ele não está incluído no ZIP.

**Não envie `instance/`, `.env`, senhas ou a pasta `.venv/` ao GitHub.** O `.gitignore` protege esses caminhos, mas confira com `git status`.

## 2. Crie um repositório público no GitHub

Acesse https://github.com/new, escolha **Repository name: `zelabairro-gs2026`**, marque **Public** e crie um repositório **vazio** (sem README, .gitignore ou license inicial, pois os arquivos já estão no projeto).

Dentro da pasta `zelabairro-mvp`:

```bash
git init
git branch -M main
git add .
git status
git commit -m "feat: MVP ZelaBairro com CI DevSecOps"
git remote add origin https://github.com/SEU_USUARIO/zelabairro-gs2026.git
git push -u origin main
```

Substitua `SEU_USUARIO` por seu username real. Caso o GitHub peça autenticação, use a autenticação do Git Credential Manager, `gh auth login` ou token com o escopo mínimo necessário — não salve tokens no repositório. Se você já tem repositório, não repita `git init` nem `git remote add`; integre os arquivos novos e faça commit/push normalmente.

## 3. O que o GitHub Actions executará automaticamente

Abra seu repositório > aba **Actions** > workflow `ZelaBairro - CI e DevSecOps`. A cada push e pull request, são executados:

| Job | O que testa | Resultado esperado |
| --- | --- | --- |
| `unit-tests` | Sintaxe e testes automatizados de cadastro/consulta/status/CSRF | Passou ou falhou |
| `gitleaks` | Verifica segredos no histórico Git | Bloqueia caso encontre segredo |
| `semgrep` | Analisa o código Python com regras de segurança | Bloqueia achados |
| `docker-trivy` | Cria container, testa `/health` e busca CVEs altas/críticas corrigíveis | Bloqueia falhas |
| `ci-validada` | Depende de todos os jobs acima | Só passa se todos passarem |

**Não declare aprovação antes do GitHub mostrar os jobs verdes.** A primeira execução pode revelar vulnerabilidades ou incompatibilidades novas; corrija o problema e gere um novo commit.

Este workflow usa `gitleaks/gitleaks-action@v3` (Node 24) e `actions/checkout@v6`. Para repositório de **organização**, o Gitleaks Action poderá exigir uma licença gratuita configurada em GitHub Secrets com nome `GITLEAKS_LICENSE`; para repositórios de conta pessoal, não é necessária a licença.

Se algum scanner reportar CVEs reais, **não desative a verificação** para deixar o workflow verde. Atualize dependências/imagem e registre a evidência da correção. Trivy está configurado para bloquear severidades HIGH/CRITICAL corrigíveis (`ignore-unfixed: true`); documente quaisquer exceções ou decisões de risco.

## 4. Demonstração oficial: execução bloqueada e corrigida

A página 41 da rubrica da FIAP exige que demonstre um pipeline barrado e o mesmo pipeline corrigido. Faça uma demonstração segura em uma branch **temporária**, sem usar senhas verdadeiras:

```bash
git switch -c demo/bloqueio-semgrep
printf 'def exemplo_inseguro():\n    return eval("2 + 2")\n' > demo_inseguro.py
git add demo_inseguro.py
git commit -m "test: demonstracao segura de bloqueio no Semgrep"
git push -u origin demo/bloqueio-semgrep
```

Na aba **Actions**, procure o run dessa branch. O Semgrep deve acusar `zelabairro-python-eval-dinamico` e reprovar o job; capture print com o nome do job e o trecho da regra.

Corrija removendo o arquivo temporário:

```bash
rm demo_inseguro.py
git add -u
git commit -m "fix: remover padrao inseguro no exemplo"
git push
```

Quando todas as verificações estiverem verdes, capture o print de correção do mesmo branch. A branch pode ser eliminada depois de registrar as evidências. **Nunca insira uma chave real para demonstrar o Gitleaks.**

Se um outro job falhar por motivo independente, primeiro corrija a dependência ou infraestrutura; não atribua esse erro ao exemplo de `eval`.

## 5. Quais evidências guardar para a entrega

Crie uma pasta local de evidências (não é necessário publicar arquivos sensíveis no Git):

- `01-commit-repositorio.png` — repositório público e arquivos da aplicação.
- `02-run-ci-completo.png` — execução com os cinco jobs aprovados.
- `03-semgrep-bloqueado.png` — achado `eval(...)` na branch de teste.
- `04-semgrep-corrigido.png` — nova execução verde na mesma branch.
- `05-docker-build.png` — log de build e smoke test.
- `06-trivy.png` — resultado de scan (sem vulnerabilidades bloqueantes ou com correção documentada).

Os prints reais e o link do repositório público entram no PDF da disciplina Secure DevOps. **Não declare que já foram capturados**.

## 6. Próximas etapas ainda obrigatórias

1. Definir o provedor de cloud e o orçamento; provisionar infraestrutura real por Terraform (state e `.tfvars` fora do Git, porta admin nunca aberta para `0.0.0.0/0`).
2. Publicar a **mesma aplicação** com HTTPS e deploy automático *após* a aprovação do pipeline; configurações e segredos via GitHub Secrets.
3. Montar Prometheus/Grafana (ou equivalente) com tráfego, latência, erros e saturação, **mais um alerta realmente disparado**.
4. Produzir o PDF de Secure DevOps com arquitetura, responsabilidade compartilhada, LGPD, custo e prints reais.
5. Em paralelo, Startup do Henio aproveita a URL do **mesmo MVP** para testes de cidadãos, modelo de negócio, Lean Canvas e pitch.

**Enunciado:** Desafio FIAP CitizenTech 4ES, GS 2026.2, pp. 18–24, 31–34, 39–41. Data-limite: 19/11/2026, às 23h55.
