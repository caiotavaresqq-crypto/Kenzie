> **Documento histórico da versão 0.8.** A partir da Kenzie 0.9, a geração principal é local (Ollama); as descrições abaixo sobre OpenRouter não refletem mais o fluxo ativo. Consulte `INTEGRACAO_COGNITIVA_v0.9.md`.

# Kenzie — Integração Cognitiva v0.8

## O que foi integrado

- `kenzie_cognition/` contém os módulos das fases 1–7 do Cognitive Transfer.
- `knowledge_pack/domains/` contém a base inicial de conhecimento local.
- `cognitive_bridge.py` conecta a análise ao core sem chamar o provedor diretamente.
- `Kenzie.py` usa a ponte em `montar_mensagens_ia()`, antes da chamada existente ao OpenRouter/OpenAI.
- Action Engine, replanejador, `memory_store.py`, interface e voz foram preservados; não houve migração do banco principal.
- A mensagem atual é inserida uma vez no conjunto de mensagens do provedor; o histórico anterior é limitado.

## Fluxo integrado

1. Captura o histórico anterior, limitado para manter o limite original.
2. Persiste a mensagem atual no histórico da Kenzie.
3. Recupera o texto de memória existente.
4. Executa análise cognitiva local (intenção, contexto, referências, ambiguidade, quadro de problema e busca opcional na base inicial).
5. Adiciona a análise como contexto auxiliar explicitamente falível e não confiável.
6. Entrega mensagens à chamada existente do modelo; OpenRouter/OpenAI permanece inalterado.
7. Se a integração estiver desativada ou falhar, usa o fluxo tradicional.

## Ativar/desativar

Por padrão, a integração está habilitada. Para desligá-la, adicione ao `.env`:


```dotenv
KENZIE_COGNITION_ENABLED=0
```

Para habilitar novamente, defina `KENZIE_COGNITION_ENABLED=1` ou remova a variável. Não apague os dados cognitivos para desativar.

## Dados separados

Criados sob demanda em `cognition_data/`:
- `kenzie_cognitive.db`: conhecimento com origem, confiança e flag de verificação.
- `learning_candidates.jsonl`: candidatos pendentes de revisão.
- `feedback_journal.jsonl`: registros explícitos de feedback.

Esses dados são separados da memória principal SQLite e dos arquivos JSON existentes. Candidatos de aprendizado não são aplicados automaticamente; uma aprovação ainda não os torna verificados.

## Testes

Na pasta `Kenzie-main`:


```bash
py -m unittest discover -s tests -v
```

Os testes cobrem Action Engine, replanejador, fases cognitivas transferidas, ponte e sinalizador de desligamento. São testes locais/simulados; não abrem apps/sites nem chamam API.

## Reversão

- Rápida: `KENZIE_COGNITION_ENABLED=0` no `.env`.
- Completa: restaurar o backup da pasta anterior. Os módulos novos são independentes e não alteram o esquema da memória principal.

## Limitações

- Compreensão e ambiguidade são heurísticas, não infalíveis.
- A integração fornece contexto auxiliar; não treina pesos do LLM.
- OpenRouter, interface/voz e ações reais do Windows não foram validados nesta sessão.
- A base inicial é local e não deve ser tratada como fonte verificada.
