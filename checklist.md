# Checklist de Pendências do Bot dYdX v4

## 1. Execução de Ordens
- [x] Envio básico de ordens de compra (buy) via API
- [ ] Envio de ordens de venda (sell)
- [ ] Suporte a ordens LIMIT e MARKET conforme parâmetros
- [ ] Implementar autenticação/assinatura (mnemonic/key) se exigido pela API
- [ ] Validação de resposta e tratamento de erros detalhado
- [ ] Validação de saldo antes de enviar ordem
- [ ] Parâmetro para ativar/desativar modo simulação (dry-run)

## 2. Monitoramento de Posições e SL/TP
- [ ] Implementar módulo `monitor.py` para monitorar posições abertas
- [ ] Consulta de posições abertas via API
- [ ] Execução automática de ordens de saída (stop-loss/take-profit)
- [ ] Lógica para ordens OCO (One Cancels Other) se suportado
- [ ] Logging detalhado de eventos de SL/TP

## 3. Estratégia e Parâmetros
- [ ] Centralizar lógica de estratégia em `strategy.py`
- [ ] Permitir ajuste dinâmico de parâmetros via CLI/config
- [ ] Implementar cálculo dinâmico de tamanho de ordem baseado em risco
- [ ] Backtesting simples da estratégia

## 4. CLI e Usabilidade
- [ ] Melhorar interface CLI (argumentos, comandos, help)
- [ ] Exibir status em tempo real (posições, PnL, ordens)
- [ ] Tooltips e mensagens amigáveis para o usuário

## 5. Logging, Monitoramento e Segurança
- [x] Logging centralizado e detalhado
- [ ] Implementar métricas de performance (acerto, drawdown, etc)
- [ ] Alertas de erro e eventos críticos
- [ ] Backup automático de configs e histórico
- [ ] Garantir que mnemonic/key nunca apareça em logs
- [ ] Testes unitários e de integração

## 6. Documentação
- [ ] Centralizar documentação de endpoints e parâmetros
- [ ] Atualizar README com exemplos reais de uso
- [ ] Documentar estrutura de arquivos e módulos

## 7. Deploy e Operação
- [ ] Script de deploy automatizado (Linux/Windows)
- [ ] Suporte a execução contínua (systemd/tmux)
- [ ] Orientações de atualização e manutenção

---

**Observação:**
- Marque cada item conforme for implementando.
- Priorize autenticação, monitoramento de posições e segurança antes de operar em ambiente real. 