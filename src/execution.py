"""
Módulo responsável pela execução de ordens na dYdX v4
"""

from typing import Dict, Optional
import logging

class Execution:
    def __init__(self, config: Dict, api_client):
        self.config = config
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    async def send_order(self, side: str, size: float, price: Optional[float] = None) -> Optional[Dict]:
        """
        Envia uma ordem de compra ou venda para a dYdX.
        side: 'buy' ou 'sell'
        size: quantidade
        price: preço limite (None para ordem a mercado)
        """
        self.logger.info(f"Enviando ordem: {side} {size} @ {price if price else 'market'}")
        payload = {
            "market": self.config['trading']['market'],
            "side": side,
            "size": size,
            "type": "MARKET" if price is None else "LIMIT",
        }
        if price is not None:
            payload["price"] = price
        # Chama o método real do api_client
        try:
            response = await self.api_client.place_order(payload)
            if response:
                self.logger.info(f"Ordem enviada com sucesso: {response}")
                return response
            else:
                self.logger.error("Falha ao enviar ordem: resposta vazia")
                return {"status": "erro", "detalhe": "resposta vazia"}
        except Exception as e:
            self.logger.error(f"Erro ao enviar ordem: {e}")
            return {"status": "erro", "detalhe": str(e)}

    def calcular_sl_tp(self, preco_entrada: float, resistencia: float) -> Dict:
        """
        Calcula os níveis de Stop-Loss e Take-Profit baseado no risco:recompensa.
        """
        risco = preco_entrada - resistencia
        sl = resistencia - risco  # Stop logo abaixo da resistência
        rr = self.config['trading']['risk_reward_ratio']
        tp = preco_entrada + abs(risco) * rr
        return {"sl": sl, "tp": tp}

    async def consultar_posicao(self) -> Optional[Dict]:
        """
        Consulta posição aberta no mercado atual.
        """
        # TODO: Implementar consulta real via API
        return None 