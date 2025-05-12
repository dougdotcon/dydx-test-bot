"""
Script para testar o cliente Cosmos da dYdX v4
"""
import asyncio
import json
import logging
from datetime import datetime
from src.cosmos_client import DydxCosmosClient

# Configura logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_cosmos_client():
    """Testa todas as funcionalidades do cliente Cosmos"""
    
    # Carrega configuração
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    logger.info("=== Iniciando testes do cliente Cosmos ===")
    logger.info(f"REST Endpoint: {config['network']['endpoints']['rest']}")
    
    try:
        async with DydxCosmosClient(config) as client:
            # 1. Teste de Status da Rede
            logger.info("\n=== 1. Testando status da rede ===")
            status = await client.get_network_status()
            if status:
                # Extrai informações relevantes
                network = status.get('node_info', {}).get('network')
                block_height = status.get('sync_info', {}).get('latest_block_height')
                catching_up = status.get('sync_info', {}).get('catching_up')
                
                logger.info(f"Network: {network}")
                logger.info(f"Latest Block: {block_height}")
                logger.info(f"Catching up: {catching_up}")
                logger.info("✓ Status obtido com sucesso")
                logger.debug(f"Status completo: {json.dumps(status, indent=2)}")
            else:
                logger.error("✗ Falha ao obter status")
            
            # 2. Teste de Bloco
            if block_height:
                logger.info(f"\n=== 2. Testando dados do bloco {block_height} ===")
                block = await client.get_latest_block()
                if block:
                    # Extrai informações relevantes
                    time = block.get('block', {}).get('header', {}).get('time')
                    proposer = block.get('block', {}).get('header', {}).get('proposer_address')
                    num_txs = len(block.get('block', {}).get('data', {}).get('txs', []))
                    
                    logger.info(f"Block Time: {time}")
                    logger.info(f"Proposer: {proposer}")
                    logger.info(f"Number of Txs: {num_txs}")
                    logger.info("✓ Dados do bloco obtidos com sucesso")
                    logger.debug(f"Bloco completo: {json.dumps(block, indent=2)}")
                else:
                    logger.error("✗ Falha ao obter dados do bloco")
            
            # 3. Teste de Dados de Mercado
            markets = ["ETH-USD", "BTC-USD", "LINK-USD"]
            for market in markets:
                logger.info(f"\n=== 3. Testando dados do mercado {market} ===")
                market_data = await client.get_market_data(market)
                if market_data:
                    logger.info("✓ Dados do mercado obtidos com sucesso")
                    logger.debug(f"Dados do mercado: {json.dumps(market_data, indent=2)}")
                    
                    # Analisa os dados encontrados
                    if isinstance(market_data, dict):
                        for key, value in market_data.items():
                            logger.info(f"{key}: {value}")
                else:
                    logger.error(f"✗ Falha ao obter dados do mercado {market}")
            
            # 4. Teste de Rate Limiting e Retries
            logger.info("\n=== 4. Testando rate limiting e retries ===")
            tasks = []
            for _ in range(5):
                tasks.append(client.get_network_status())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"Requests bem sucedidos: {success} de {len(results)}")
            
            if success > 0:
                logger.info("✓ Rate limiting funcionando corretamente")
            else:
                logger.error("✗ Todas as requisições falharam")
            
    except Exception as e:
        logger.error(f"Erro fatal durante os testes: {e}")
        raise

def main():
    """Função principal"""
    try:
        asyncio.run(test_cosmos_client())
        logger.info("\n=== Testes concluídos! ===")
        
    except KeyboardInterrupt:
        logger.info("\n! Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"\n✗ Erro fatal: {e}")
    finally:
        logger.info("\nSessão de testes finalizada")

if __name__ == "__main__":
    main()