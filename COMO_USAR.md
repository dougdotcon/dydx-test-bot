# 🚀 Como Usar o dYdX Trading Bot

## 📋 Pré-requisitos

### 1. **Python 3.10+**
```bash
python --version  # Deve ser 3.10 ou superior
```

### 2. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 3. **Configurar Variáveis de Ambiente** (Opcional para modo real)
```bash
# Copie o arquivo de exemplo
cp config/.env.example .env

# Edite o arquivo .env com suas credenciais
DYDX_MNEMONIC="sua mnemonic aqui"
```

---

## 🎮 Modo Simulação (Recomendado para Começar)

### **Teste Rápido**
```bash
# Teste a estrutura
python test_structure.py

# Teste integração completa
python test_integration.py
```

### **Iniciar Bot em Simulação**
```bash
# Usando CLI
python main.py start --simulation --market ETH-USD --position-size 100

# Ou usando o bot diretamente
python bot.py
```

### **Verificar Status**
```bash
python main.py status
```

---

## 🔧 Comandos CLI Disponíveis

### **Iniciar o Bot**
```bash
python main.py start [OPTIONS]

Opções:
  --market TEXT           Mercado para operar (default: ETH-USD)
  --position-size FLOAT   Tamanho da posição em USD (default: 100.0)
  --simulation            Executar em modo simulação
  --timeframe TEXT        Timeframe dos candles (default: 5m)
  --help                  Mostrar ajuda
```

### **Configuração Inicial**
```bash
python main.py setup
```

### **Verificar Status**
```bash
python main.py status
```

---

## 📊 Estrutura de Dados

### **Trades Salvos**
Os trades são automaticamente salvos em `data/trades.json`:
```json
{
  "market": "ETH-USD",
  "side": "LONG",
  "entry_price": 2000.0,
  "exit_price": 2100.0,
  "pnl": 10.0,
  "timestamp": "2024-01-01T12:00:00"
}
```

### **Métricas de Performance**
Calculadas automaticamente em `data/performance.json`:
```json
{
  "total_trades": 10,
  "total_pnl": 150.0,
  "win_rate": 70.0,
  "profit_factor": 1.5,
  "max_drawdown": 50.0
}
```

### **Logs**
Logs detalhados em `logs/dydx_bot.log`

---

## ⚙️ Configurações Principais

### **Arquivo: `src/core/config.py`**
```python
# Mercado padrão
DEFAULT_MARKET = "ETH-USD"

# Tamanho da posição em USD
DEFAULT_POSITION_SIZE_USD = 100.0

# Timeframe dos candles
DEFAULT_TIMEFRAME = "5m"

# Parâmetros da estratégia
DEFAULT_VOLUME_FACTOR = 1.5
DEFAULT_RESISTANCE_PERIODS = 20
DEFAULT_RISK_REWARD_RATIO = 2.0
```

### **Parâmetros de Risco**
```python
# Tamanho máximo de posição
MAX_POSITION_SIZE_USD = 1000.0

# Drawdown máximo permitido
MAX_DRAWDOWN_PERCENT = 10.0

# Perda diária máxima
MAX_DAILY_LOSS_USD = 500.0
```

---

## 🛡️ Sistema de Risco

### **Validações Automáticas**
- ✅ **Saldo suficiente** antes de abrir posições
- ✅ **Margem disponível** para a operação
- ✅ **Tamanho de posição** dentro dos limites
- ✅ **Drawdown** não excede o máximo
- ✅ **Perda diária** dentro dos limites

### **Circuit Breaker**
O bot para automaticamente se:
- Perda diária exceder o limite
- Drawdown exceder o máximo
- Saldo insuficiente para operar

---

## 📈 Estratégia de Trading

### **Breakout Strategy**
1. **Detecta níveis de resistência** nos últimos 20 períodos
2. **Aguarda breakout** do preço acima da resistência
3. **Confirma com volume** (1.5x a média)
4. **Abre posição long** no breakout
5. **Define stop-loss** abaixo da resistência
6. **Define take-profit** com ratio 2:1

### **Condições de Entrada**
- Preço > Nível de Resistência
- Volume > 1.5x Volume Médio
- Saldo suficiente
- Sem circuit breaker ativo

### **Condições de Saída**
- Stop-loss atingido
- Take-profit atingido
- Sinal manual de fechamento

---

## 🔍 Monitoramento

### **Logs em Tempo Real**
```bash
tail -f logs/dydx_bot.log
```

### **Verificar Trades**
```bash
# Ver trades salvos
cat data/trades.json | python -m json.tool

# Ver métricas
cat data/performance.json | python -m json.tool
```

### **Status do Bot**
```bash
python main.py status
```

---

## 🚨 Troubleshooting

### **Erro de Import**
```bash
# Verificar se todas as dependências estão instaladas
pip install -r requirements.txt

# Testar imports
python test_structure.py
```

### **Erro de Conexão dYdX**
```bash
# Verificar se está em modo simulação
python main.py start --simulation

# Verificar credenciais (se modo real)
cat .env
```

### **Bot Não Abre Posições**
- Verificar se há sinal de breakout
- Verificar saldo disponível
- Verificar se circuit breaker não está ativo
- Verificar logs para detalhes

### **Dados Não Salvam**
- Verificar permissões da pasta `data/`
- Verificar espaço em disco
- Verificar logs para erros

---

## 📞 Suporte

### **Logs Detalhados**
Para debug, ative logs detalhados:
```python
# Em config.py
LOG_LEVEL = "DEBUG"
```

### **Testes**
```bash
# Teste completo
python test_integration.py

# Teste específico
python test_structure.py
```

### **Reset Completo**
```bash
# Limpar dados (cuidado!)
rm -rf data/*.json
rm -rf logs/*.log

# Reiniciar
python main.py setup
```

---

## 🎯 Próximos Passos

1. **Teste em simulação** até se familiarizar
2. **Configure credenciais** dYdX para testes reais
3. **Teste com valores pequenos** no testnet
4. **Monitore performance** e ajuste parâmetros
5. **Expanda funcionalidades** conforme necessário

**Boa sorte com seu trading automatizado! 🚀**
