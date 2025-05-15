# dYdX v4 Trading Bot - Breakout Strategy

Um bot de trading simples para a dYdX v4 testnet que implementa uma estratégia de breakout com confirmação de volume.

## Visão Geral

Este bot monitora o mercado da dYdX v4 testnet em busca de oportunidades de breakout, onde o preço rompe um nível de resistência com volume anormalmente alto. Quando um sinal de breakout é detectado, o bot abre uma posição long e define automaticamente os níveis de stop-loss e take-profit com base em uma proporção de risco:recompensa de 1:3.

## Características

- Monitoramento de dados de mercado em tempo real via API REST
- Detecção de sinais de breakout quando o preço rompe a resistência com volume alto
- Cálculo automático de níveis de stop-loss e take-profit usando proporção de risco:recompensa de 1:3
- Execução e gerenciamento de posições (simulado por enquanto)
- Interface de linha de comando para fácil configuração e controle
- Modo de simulação para testar sem colocar ordens reais

## Estrutura do Projeto

```
dydx_bot/
├── dydx_api.py          # Cliente da API dYdX v4
├── breakout_strategy.py # Implementação da estratégia de breakout
├── position_manager.py  # Gerenciamento de posições
├── bot.py               # Implementação principal do bot
├── run_bot.py           # Script para executar o bot por um período específico
├── test_bot.py          # Script de teste
├── requirements.txt     # Dependências do projeto
└── README_DYDX_BOT.md   # Documentação
```

## Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/yourusername/dydx-trading-bot.git
   cd dydx-trading-bot
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Uso

### Testando o Bot

Para testar o bot e verificar se ele pode se conectar à API da dYdX v4 testnet:

```
python test_bot.py
```

### Iniciando o Bot

```
python bot.py [OPÇÕES]
```

Opções:
- `--market TEXT`: Símbolo do mercado (ex: "ETH-USD") [padrão: ETH-USD]
- `--timeframe TEXT`: Timeframe das velas (ex: "1MIN", "5MINS", "15MINS", "30MINS", "1HOUR", "4HOURS", "1DAY") [padrão: 1MIN]
- `--volume-factor FLOAT`: Fator de volume para confirmação de breakout [padrão: 2.0]
- `--resistance-periods INTEGER`: Número de períodos para olhar para trás para resistência [padrão: 24]
- `--risk-reward FLOAT`: Proporção de risco:recompensa para cálculo de take profit [padrão: 3.0]
- `--position-size FLOAT`: Tamanho da posição em USD [padrão: 100.0]
- `--update-interval INTEGER`: Intervalo em segundos entre atualizações de dados de mercado [padrão: 60]
- `--api-url TEXT`: URL da API da dYdX [padrão: https://dydx-testnet.imperator.co/v4]

Exemplo:
```
python bot.py --market ETH-USD --timeframe 1MIN --volume-factor 2.0 --position-size 100 --update-interval 30
```

### Executando o Bot por um Período Específico

Para executar o bot por um período específico (por exemplo, 1 hora):

```
python run_bot.py --duration 3600 [OUTRAS OPÇÕES]
```

Opções adicionais:
- `--duration INTEGER`: Duração em segundos para executar o bot (0 para indefinido) [padrão: 3600]

Exemplo:
```
python run_bot.py --market ETH-USD --timeframe 1MIN --update-interval 30 --duration 1800
```

## Melhorias Implementadas

1. **Correção dos endpoints da API**: Atualizamos os endpoints da API para usar a URL correta da dYdX v4 testnet.
2. **Suporte para diferentes timeframes**: Adicionamos suporte para diferentes timeframes de velas (1MIN, 5MINS, 15MINS, etc.).
3. **Intervalo de atualização configurável**: Adicionamos a opção de configurar o intervalo entre atualizações de dados de mercado.
4. **Execução por tempo limitado**: Adicionamos a opção de executar o bot por um período específico.
5. **Melhor tratamento de erros**: Melhoramos o tratamento de erros e a recuperação de falhas.

## Limitações Atuais

- O bot está em modo de simulação e não coloca ordens reais
- Não há autenticação implementada para colocar ordens reais
- A detecção de breakout pode gerar falsos positivos em mercados voláteis

## Próximos Passos

1. **Implementar autenticação**: Adicionar suporte para autenticação com a API da dYdX v4 para colocar ordens reais.
2. **Melhorar a detecção de breakout**: Refinar o algoritmo de detecção de breakout para reduzir falsos positivos.
3. **Adicionar suporte para posições short**: Implementar suporte para abrir posições short em breakdowns de suporte.
4. **Adicionar backtesting**: Implementar funcionalidade de backtesting para avaliar a estratégia em dados históricos.
5. **Melhorar o gerenciamento de risco**: Adicionar mais opções de gerenciamento de risco, como trailing stop.
6. **Interface web**: Adicionar uma interface web para monitorar e controlar o bot.

## Referências

- [Documentação oficial da dYdX v4](https://docs.dydx.exchange/)
- [API da dYdX v4](https://docs.dydx.exchange/developers/indexer/indexer-api-reference)
- [Guia de Estratégia de Breakout](guia.md)

## Licença

MIT
