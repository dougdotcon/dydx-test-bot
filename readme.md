# Bot de Trading dYdX v4 (Testnet)

## Introdução

Este projeto implementa um bot de trading automatizado para a dYdX v4 (testnet). O bot monitora o mercado, detecta possíveis breakouts (baseado em preço e anomalia de volume) e executa ordens de compra (buy) via API REST. O projeto é modular, extensível e segue as melhores práticas de desenvolvimento (logging, tratamento de erros, CLI, etc).

## Requisitos

- Python 3.8 (ou superior)
- Pip (gerenciador de pacotes)
- Conta na dYdX v4 (testnet) (para operar em ambiente de teste)
- (Opcional) Mnemônico (ou chave privada) para autenticação (caso a API exija)

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositório>
   cd <nome-do-diretório>
   ```

2. Crie um ambiente virtual (recomendado) e ative-o:
   - **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\Activate.ps1
     ```
   - **Linux/Mac:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

O bot utiliza um arquivo de configuração (`config/config.json`) para definir parâmetros de rede, endpoints, estratégia, trading, logging, etc. Exemplo de configuração:

```json
{
  "network": {
    "endpoints": {
      "rest": "https://api.dydx.exchange (ou endpoint da testnet)",
      "ws": "wss://indexer.dydx.exchange (ou endpoint da testnet)"
    }
  },
  "trading": {
    "market": "ETH-USD",
    "volume_factor": 1.5,
    "risk_reward_ratio": 2.0
  },
  "logging": {
    "level": "INFO",
    "file": "bot.log"
  },
  "debug": {
    "ssl_verify": true
  }
}
```

**Observação:**  
- Ajuste o endpoint para a testnet (ou produção) conforme necessário.
- Se a API exigir autenticação, adicione a mnemonic (ou chave) em um arquivo `.env` (nunca em logs ou no código).

## Execução

Para iniciar o bot, execute o módulo principal:

```bash
python -m src.bot
```

O bot inicia o loop principal, monitora o mercado e, ao detectar um breakout (preço acima da resistência e volume anômalo), envia uma ordem de compra (buy) via API.  
O resultado da ordem (sucesso ou erro) é registrado no log (`bot.log`).

## Estrutura de Arquivos e Módulos

- **`src/`**  
  - **`bot.py`:** Loop principal, integração dos módulos e execução do bot.  
  - **`market_data.py`:** Coleta e analisa dados de mercado (preço, volume, resistência).  
  - **`execution.py`:** Envio de ordens (compra/venda) via API.  
  - **`api_client.py`:** Cliente HTTP (aiohttp) para comunicação com a API dYdX.  
  - **`utils.py`:** Funções auxiliares (logging, carregamento de configuração, validação).  
  - **`strategy.py`:** (Pendente) Centralização da lógica de estratégia.  
  - **`monitor.py`:** (Pendente) Monitoramento de posições abertas e SL/TP.

- **`config/`**  
  - **`config.json`:** Arquivo de configuração (endpoints, parâmetros de trading, logging, etc).

- **`checklist.md`:** Lista de pendências e próximos passos do projeto.

## Checklist de Pendências

Consulte o arquivo [checklist.md](checklist.md) para um panorama completo de pendências, incluindo:

- Execução de ordens (ordens de venda, autenticação, dry-run, validação de saldo, etc).
- Monitoramento de posições e SL/TP (módulo `monitor.py`, consulta de posições, ordens OCO).
- Estratégia e parâmetros (centralização, ajuste dinâmico, cálculo de tamanho de ordem, backtesting).
- CLI e usabilidade (interface, status em tempo real, tooltips).
- Logging, monitoramento e segurança (métricas, alertas, backup, proteção de mnemonic, testes).
- Documentação (centralização, exemplos reais, estrutura dos módulos).
- Deploy e operação (scripts, execução contínua, manutenção).

## Segurança

- **Autenticação:**  
  Se a API dYdX exigir autenticação (mnemonic ou chave privada), armazene-a em um arquivo `.env` (nunca em logs ou no código).  
- **Modo Simulação (Dry-Run):**  
  Recomenda-se implementar um parâmetro (ou flag) para ativar/desativar o modo simulação, evitando ordens acidentais em ambiente real.  
- **Logs e Dados Sensíveis:**  
  Garanta que dados sensíveis (mnemonic, chaves) nunca sejam registrados em logs.

## Documentação

- **Endpoints e Parâmetros:**  
  A documentação dos endpoints e parâmetros da API dYdX v4 deve ser centralizada (por exemplo, em um arquivo `docs/api.md`).  
- **README:**  
  Este README.md serve como guia inicial. Atualize-o com exemplos reais de uso, instruções de deploy e manutenção.  
- **Estrutura de Arquivos:**  
  Documente a função de cada módulo e a interação entre eles.

## Testes

- **Testes Unitários:**  
  Implemente testes unitários (por exemplo, com `pytest`) para validar a lógica de cada módulo.  
- **Testes de Integração:**  
  Teste o fluxo completo (detecção de breakout, envio de ordem, monitoramento) em ambiente de testnet.

## Deploy e Operação

- **Scripts de Deploy:**  
  Crie scripts (ou instruções) para automatizar o deploy em ambientes Linux/Windows.  
- **Execução Contínua:**  
  Utilize ferramentas como `systemd` (Linux) ou `tmux` (Windows) para manter o bot rodando continuamente.  
- **Atualização e Manutenção:**  
  Documente o processo de atualização (pull, atualizar dependências, reiniciar) e manutenção (logs, alertas).

## Contato e Contribuições

- **Issues e Pull Requests:**  
  Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções ou novas funcionalidades.  
- **Contato:**  
  [Seu e-mail ou perfil de contato]

---

**Observação:**  
Este README.md é um guia inicial e deve ser atualizado conforme o projeto evolui.  
Consulte o [checklist.md](checklist.md) para acompanhar as pendências e próximos passos. 