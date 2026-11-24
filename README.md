# Kenzie Core 1.0-alpha

Primeira arquitetura integrada modular. Python 3.10+; biblioteca padrão apenas.

## Executar
```bash
python main.py
```
Testes:
```bash
python -m unittest discover -s tests -v
```

## Implementado nesta versão
- Orquestrador central e CLI.
- Conhecimento-base de matemática, ciências, tecnologia e conceitos gerais.
- Grafo de conceitos, relações e busca de caminhos.
- Raciocínio relacional limitado e recuperação de fatos.
- Memória episódica, semântica, procedural e contextual (armazenamento JSON).
- Aprendizado supervisionado explícito por correções/ensino.
- Planejador básico de tarefas.
- Monitor de confiança e lacunas.
- Calculadora com AST allowlist (sem `eval`).
- Simulações determinísticas simples (juros compostos e crescimento populacional).
- Ações locais allowlist, sem execução arbitrária de shell.
- Registro de auditoria e validação de entrada.
- Registro básico de especialistas.
- Adaptadores opcionais OpenRouter/Ollama por variável de ambiente.
- Camadas de percepção com pontos de extensão para áudio, imagem e vídeo.

## Configuração opcional de modelos
Por padrão, nenhum modelo externo é chamado. Para OpenRouter:
```cmd
set KENZIE_PROVIDER=openrouter
set OPENROUTER_API_KEY=sua_chave
set OPENROUTER_MODEL=apodex/apodex-1.1-mini:free
python main.py
```
Para Ollama:
```cmd
set KENZIE_PROVIDER=ollama
set OLLAMA_MODEL=qwen2.5-coder:1.5b
python main.py
```
O adaptador está isolado; o Core funciona sem esses serviços.

## Limites importantes
Esta não é uma IA geral, não possui consciência, não treina pesos neurais e não aprende autonomamente sem supervisão.
O aprendizado atual registra exemplos/correções e experiências; não modifica o código-fonte nem se autoatualiza.
Raciocínio e planejamento são limitados e transparentes. Pesquisa web, visão, áudio, vídeo, fala, execução de código isolada,
treinamento neural, busca semântica vetorial e especialistas autônomos exigem implementações e testes posteriores.
Não use dados pessoais ou credenciais em exemplos de aprendizado.
