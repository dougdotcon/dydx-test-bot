<div align="center">
  <img src="logo.png" alt="dYdX Trading Bot Logo" width="300">
</div>

# Documentação do Bot de Trading dYdX v4

Bem-vindo à documentação do Bot de Trading dYdX v4. Esta documentação fornece informações completas sobre a arquitetura, configuração, uso e desenvolvimento do bot.

---

## 📋 Como Usar o Bot de Trading dYdX

O bot de trading dYdX é uma ferramenta automatizada para monitorar e executar operações no mercado de criptomoedas dYdX v4. Abaixo estão as instruções para executar o bot:

### Requisitos
* Python instalado
* Dependências instaladas (execute `pip install -r requirements.txt`)
* Conta na dYdX v4 configurada

### 🚀 Executando o Bot

Para iniciar o bot, use o seguinte comando no terminal:

```bash
python bot.py --market [PAR-DE-MOEDAS] --timeframe [PERÍODO] --update-interval [SEGUNDOS] --position-size [VALOR]
```

**Parâmetros:**
* `--market`: Par de moedas para operar (ex: ETH-USD, BTC-USD)
* `--timeframe`: Período do gráfico (ex: 1MIN, 5MIN, 15MIN, 1H)
* `--update-interval`: Intervalo em segundos para atualização dos dados (ex: 30)
* `--position-size`: Tamanho da posição em dólares (ex: 100)

**Exemplo:**
```bash
python bot.py --market ETH-USD --timeframe 1MIN --update-interval 30 --position-size 100
```

### 💡 Funcionamento
O bot monitora o mercado em busca de oportunidades de breakout (rompimento) com confirmação de volume. Quando identifica uma oportunidade, executa automaticamente a operação de acordo com os parâmetros configurados.

### 📊 Monitoramento
Durante a execução, o bot exibe informações como:
* Nível de resistência atual
* Volume médio
* Preço atual
* Oportunidades de trading identificadas

Para interromper o bot, pressione `Ctrl+C` no terminal.

### ⚙️ Parâmetros Avançados
Além dos parâmetros básicos, o bot utiliza os seguintes parâmetros avançados que podem ser configurados:

* **Fator de Volume**: Fator multiplicador para confirmação de volume (padrão: 2.0)
* **Períodos de Resistência**: Número de períodos para cálculo de resistência (padrão: 24)
* **Relação Risco:Recompensa**: Relação risco/recompensa para definição de alvos e stop loss (padrão: 3.0)

Estes parâmetros podem ser modificados no arquivo de configuração ou através de argumentos adicionais na linha de comando.

---

## 📚 Estrutura da Documentação

* **[Primeiros Passos](guides/getting-started.md)**: Guia rápido para configurar e executar o bot
* **[Configuração](guides/configuration.md)**: Informações detalhadas sobre a configuração do bot
* **[Estratégias de Trading](guides/strategies.md)**: Documentação das estratégias de trading disponíveis
* **[Referência da API](api/README.md)**: Documentação de referência para a API dYdX v4
* **[Guia de Desenvolvimento](development/README.md)**: Guia para desenvolvedores que desejam estender ou modificar o bot
* **[Status do Projeto](development/status.md)**: Status atual do projeto e roadmap

---

## ✨ Principais Recursos

* 📡 Monitoramento de dados de mercado em tempo real via WebSocket e API REST
* 📈 Estratégia de trading de breakout com confirmação de volume
* 🛡️ Gerenciamento de risco com dimensionamento configurável de posições
* 🧪 Modo de simulação para testes sem colocar ordens reais
* 📝 Registro abrangente e histórico de negociações
* 🧩 Arquitetura modular para fácil extensão

---

## 🔗 Links Rápidos

* [Repositório do Projeto](https://github.com/yourusername/dydx_automate)
* [Documentação Oficial dYdX v4](https://docs.dydx.exchange/)
* [Rastreador de Problemas](https://github.com/yourusername/dydx_automate/issues)

---

## 👥 Contribuindo

Contribuições são bem-vindas! Consulte o [Guia de Desenvolvimento](development/README.md) para obter informações sobre como contribuir para o projeto.
