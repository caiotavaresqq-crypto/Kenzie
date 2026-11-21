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

OLLAMA
A arquitetura atual mantém o provedor de IA isolado na configuração. O Ollama ainda não está ativado neste pacote; será conectado como provedor local em uma etapa separada, depois de instalado e testado neste computador.

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

OLLAMA LOCAL — INTEGRACAO v1
----------------------------
O Ollama agora é o provedor principal da Kenzie, usando a API local compatível
com OpenAI em http://127.0.0.1:11434/v1.

MODELOS CONFIGURADOS
- Qwen3 1.7B (qwen3:1.7b): conversação geral.
- Qwen2.5-Coder 1.5B (qwen2.5-coder:1.5b): programação e depuração.
- Llama 3.2 1B (llama3.2:1b): modelo reserva local.

ROTEAMENTO E FALLBACK
- A Kenzie escolhe o Qwen Coder quando identifica uma solicitação de programação.
- Para conversa e tarefas gerais, usa o Qwen3.
- Se o modelo selecionado falhar, tenta o outro modelo principal e depois o Llama.
- Se todos os modelos locais falharem, tenta OpenRouter; se não houver OpenRouter,
  tenta OpenAI quando configurada.
- Se nenhum provedor estiver disponível, mantém as respostas offline já existentes.
- Os modelos são chamados sob demanda; a Kenzie não mantém os três carregados
  simultaneamente por conta própria.

REQUISITOS E TESTE
1. Instale e inicie o Ollama para Windows.
2. Confirme no CMD: ollama list
3. Confirme que aparecem qwen3:1.7b, qwen2.5-coder:1.5b e llama3.2:1b.
4. Opcionalmente teste a API local: ollama run qwen3:1.7b
5. Inicie a Kenzie com INICIAR_KENZIE.bat. O terminal informa qual modelo foi
   escolhido para cada solicitação e quando ocorre fallback.

CONFIGURAÇÃO
As opções podem ser alteradas no .env:
- OLLAMA_ENABLED=true
- OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
- OLLAMA_GENERAL_MODEL=qwen3:1.7b
- OLLAMA_CODER_MODEL=qwen2.5-coder:1.5b
- OLLAMA_FALLBACK_MODEL=llama3.2:1b
- OLLAMA_TIMEOUT=120
A chave OPENROUTER_API_KEY é opcional e serve apenas como fallback online.
Não é necessária chave de API para usar o Ollama local.

ATUALIZAR SEM PERDER DADOS
Extraia esta versão em uma pasta nova. Copie o .env e kenzie_memory.db da pasta
anterior para a nova. Não substitua seu .env pelo .env.example e nunca compartilhe
sua chave de API.

VALIDAÇÃO DESTA ENTREGA
Os arquivos Python foram compilados com py_compile e o arquivo ZIP foi validado.
A chamada real aos modelos depende do Ollama estar instalado e em execução no
computador Windows; essa reprodução não foi executada neste ambiente.


CONFIGURACAO DE IA — OPENROUTER + CODER LOCAL
- Conversas gerais são enviadas diretamente à OpenRouter.
- Pedidos identificados como programação tentam primeiro qwen2.5-coder:1.5b no Ollama.
- Se o modelo local falhar, a solicitação segue para a OpenRouter.
- Qwen3 e Llama não são mais usados nem chamados pelo código.
- Configure OPENROUTER_API_KEY no arquivo .env; mantenha OLLAMA_ENABLED=true
  para usar o modelo local de programação.
