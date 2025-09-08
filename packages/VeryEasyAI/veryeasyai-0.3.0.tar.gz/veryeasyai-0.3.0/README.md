# VeryEasyAI

VeryEasyAI é um exemplo simples de inteligência artificial (IA) que responde perguntas de forma automática. Ele foi criado para ser fácil de entender, até mesmo para quem não tem conhecimento técnico em programação.

## Como funciona?

O VeryEasyAI pode:
- Criar IAs com redes neurais.
- Responder perguntas simples sobre temas conhecidos, como "Qual a capital do Brasil?" ou "O que é inteligência artificial?".
- Ou você mesmo pode usar e criar e treinar seus próprios datasets
- Fazer buscas na internet para tentar encontrar respostas para perguntas que não conhece, usando o DuckDuckGo.

## Principais Arquivos

- **example.py**: Exemplo de uso. Mostra como conversar com a IA.
- **veryeasyai/hybrid.py**: Principal lógica da IA, define como ela entende e responde perguntas.
- **veryeasyai/nn.py**: Um modelo simples de rede neural, que tenta identificar o tipo da sua pergunta.
- **veryeasyai/knowledge.py**: Uma pequena base de conhecimento com algumas respostas prontas.
- **veryeasyai/search.py**: Faz buscas na internet para perguntas que a IA não sabe responder diretamente.

## Como usar

1. Instale os requisitos (se necessário, como o módulo `requests`).
2. Execute o arquivo `example.py` para ver exemplos de perguntas e respostas.

```bash
python -m veryeasyai.example.py
```

## Exemplos de perguntas que você pode fazer

- "oi"
- "qual a capital do brasil"
- "explique inteligência artificial"
- "pesquise no google programação python"

## IMPORTANTES ABAIXO:
Os arquivos devem ser executados com: python -m veryeasyai.Nome do arquivo(Sem .py no final.)
EXECUTE ESSES 2 ARQUIVOS ANTES DE RODAR EXEMPLO:nn.py,  hybrid.py
Este projeto é apenas para fins educacionais e demonstra como criar uma IA simples e fácil de entender.
