KENZIE - CORE v0.4 + OPENROUTER

CONTEUDO
- Kenzie.py: lógica da assistente e integração com IA.
- interface.py: interface gráfica atual.
- kenzie_core_v04.py: núcleo visual v0.4.
- tools.py: ferramentas locais do Windows.
- INICIAR_KENZIE.bat: inicializador.
- .env.example: modelo de configuração da chave (não contém chave real).

INSTALACAO
1. Extraia todos os arquivos para uma mesma pasta.
2. Instale as dependências usadas pelo projeto: PySide6, python-dotenv e openai.
3. Para instalar a voz neural offline, execute INSTALAR_VOZ_PIPER.bat e aguarde o download do modelo (cerca de 63 MB). O pyttsx3 continua como alternativa.
4. Copie .env.example e renomeie a cópia para .env.
5. Abra .env e preencha OPENROUTER_API_KEY com sua chave da OpenRouter.
6. Execute INICIAR_KENZIE.bat.

IDENTIDADE E MEMORIA
- A identidade da assistente é fixa: ela se chama Kenzie e é a camada conversacional da assistente para Windows 10.
- A memória separa nome completo do usuário, forma de tratamento preferida, nome do projeto, descrição do projeto e papel da Kenzie.
- Comandos como "Atribua meu nome a Caio Tavares e me chame de senhor" salvam o nome e o tratamento em campos diferentes.
- A forma de tratamento salva é incluída nas instruções enviadas ao modelo em todas as respostas.
- Frases como "Meu nome é Caio e estou desenvolvendo um projeto chamado Kenzie" são interpretadas em partes, sem salvar a frase inteira como nome.
- A memória é persistida em kenzie_memory.json, na pasta do projeto.
- O histórico também registra comandos de memória para manter a conversa coerente.

IA ONLINE
- A integração usa a API compatível com OpenAI da OpenRouter.
- Por padrão, usa model="openrouter/free", que seleciona um modelo gratuito disponível.
- Para fixar um modelo, defina OPENROUTER_MODEL no .env com um ID válido da OpenRouter.
- O limite de saída foi aumentado para 900 tokens.
- Se o provedor não retornar texto, a Kenzie informa a situação em vez de exibir "None".
- Erros detalhados da API são registrados no terminal; a interface recebe uma mensagem amigável.

SEGURANCA
- Nunca compartilhe seu arquivo .env nem envie sua chave para o GitHub.
- O .gitignore já exclui .env e a memória local.
- O pacote não contém sua chave de API.

TESTE RAPIDO DE MEMORIA
Depois de iniciar a Kenzie, envie estas mensagens:
1. Meu nome é Caio e estou desenvolvendo um projeto chamado Kenzie.
2. Você agora faz parte desse projeto.
3. Qual é o nome do meu projeto e o que estamos fazendo?
4. Qual é meu nome?
5. Como você deve me chamar?
6. Feche e abra a Kenzie e repita as perguntas 3, 4 e 5 para confirmar a persistência.

Se quiser corrigir os dados, envie: "Atribua meu nome a Caio Tavares e me chame de senhor". A Kenzie deve confirmar que salvou os dois campos.

OBSERVACOES
- O .env é carregado pela pasta onde Kenzie.py está localizado, mesmo que o CMD seja aberto em outro diretório.
- A memória também é salva na pasta do projeto.
- O núcleo visual e a interface foram preservados a partir do pacote-base recebido.


MEMÓRIA DE LONGO PRAZO (SQLite)
- Fatos e histórico são armazenados localmente em kenzie_memory.db.
- O banco é consultado em toda chamada à IA para recuperar fatos relevantes.
- As últimas 20 mensagens são restauradas quando a Kenzie inicia.
- kenzie_memory.json continua como cópia de compatibilidade.
- Para guardar um fato explicitamente, diga: “Lembre que ...”.
- Para consultar informações salvas, diga: “O que você lembra?”.
- Faça backup de kenzie_memory.db junto com o projeto.

PERSONALIDADE DA KENZIE
-----------------------
A personalidade agora fica no arquivo personality.py, separado da memória SQLite.
Ela define um estilo conversacional natural, acolhedor, curioso, bem-humorado,
energético e honesto, inspirado no estilo de conversa do ChatGPT, mas mantendo a
identidade própria da Kenzie. O módulo é carregado automaticamente pelo Kenzie.py
em toda chamada ao modelo de IA. Apagar o banco de memória não apaga a personalidade.

ATUALIZAÇÃO SEM PERDER DADOS
----------------------------
Ao instalar esta versão em uma pasta nova, copie também os arquivos .env e
kenzie_memory.db da instalação que já está funcionando. Não compartilhe seu .env
nem sua chave de API. Se preferir atualizar na pasta atual, faça antes uma cópia
de segurança e substitua apenas os arquivos incluídos neste pacote.

ARQUIVOS NOVOS/ALTERADOS
------------------------
- personality.py: personalidade central e independente.
- Kenzie.py: injeta as instruções de personalidade no prompt do modelo.


KENZIE VOICE v2 — PIPER NEURAL OFFLINE
------------------------------------
- Motor principal: Piper TTS, síntese neural local/offline.
- Voz inicial: Cadu, português brasileiro, qualidade média (modelo ONNX de aproximadamente 63 MB).
- Instalação: execute INSTALAR_VOZ_PIPER.bat uma vez com internet; depois a síntese funciona offline.
- A barra de conversa permite alternar entre os perfis TARS e CASE.
- TARS usa ritmo um pouco mais ágil e maior variação; CASE é mais contido e uniforme.
- O botão 🔊/🔇 ativa ou silencia a fala; ■ interrompe a reprodução.
- pyttsx3 permanece como fallback caso o Piper/modelo não esteja disponível.
- Não é necessário microfone.

AJUSTES OPCIONAIS NO .env
KENZIE_VOICE_RATE=175
KENZIE_VOICE_VOLUME=0.95
KENZIE_VOICE_PROFILE=TARS

Observação: os perfis são ajustes de ritmo e variação da síntese, não imitações exatas das vozes dos personagens. A semelhança final depende também do modelo de voz escolhido.

PROVEDOR DE IA — OPENROUTER
--------------------------
- Qwen2.5-Coder e a integração com Ollama foram removidos deste pacote.
- Conversas gerais, programação e depuração utilizam o provedor online configurado.
- OpenRouter é prioritária; OpenAI é usada como alternativa quando configurada.
- Configure OPENROUTER_API_KEY no arquivo .env.
- Para fixar um modelo, defina OPENROUTER_MODEL com um ID válido da OpenRouter.
- Se nenhum provedor online estiver disponível, a Kenzie usa as respostas offline existentes.

CONFIGURAÇÃO
- OPENROUTER_API_KEY= sua chave da OpenRouter
- OPENROUTER_MODEL=openrouter/free (opcional)
- OPENAI_API_KEY= (opcional, como alternativa)
- OPENAI_MODEL=gpt-4o-mini (opcional)


KENZIE ACTION ENGINE 0.1 (NOVO)
---------------------------------
Arquivos adicionados:
- action_engine.py: planner-schema, validação de planos e executor sequencial.
- action_engine_models.py: modelos de ferramenta, etapa e plano.
- action_engine_registry.py: registro dinâmico de ferramentas.
- action_engine_tools.py: ferramentas iniciais e allowlists.

Integração:
- Kenzie.py usa o Action Engine nas chamadas de ferramentas da IA.
- O LLM pode propor um plano multi-etapas ou chamar uma ferramenta diretamente.
- A execução é limitada às ferramentas registradas e permissões locais do engine.
- Feedback da execução é enviado à IA para uma resposta natural; a Kenzie não deve inventar sucesso.

Ferramentas 0.1:
- open_app: Calculadora, Bloco de Notas, Paint, Explorador, Gerenciador de Tarefas e VS Code (se instalado).
- open_url: valida HTTP/HTTPS e abre pelo navegador padrão.
- search_web: abre uma pesquisa Google no navegador; não simula nem extrai resultados.
- search_files: pesquisa por nome nas pastas Documentos, Desktop e Downloads; até 25 resultados.

Limitações iniciais:
- search_web apenas abre a página de pesquisa; leitura automatizada de resultados ainda não implementada.
- A busca por arquivos é limitada às pastas configuradas e a nomes de arquivos, não ao conteúdo.
- O replanejamento automático após falhas ainda não está implementado na 0.1.
- O conjunto de aplicativos é uma allowlist inicial; novos apps precisam ser autorizados no código.
