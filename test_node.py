"""
Script para testar todas as funcionalidades necessárias do node RPC Tendermint
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from src.rpc_client import DydxRpcClient

# Configura logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_node():
    """Testa todas as funcionalidades do node RPC"""
    
    # Carrega configuração
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    logger.info("=== Iniciando testes do node RPC ===")
    logger.info(f"Endpoint: {config['network']['endpoints']['rest']}")
    
    try:
        async with DydxRpcClient(config) as client:
            # 1. Teste de Status da Rede
            logger.info("\n=== 1. Testando status do node ===")
            status = await client.get_network_status()
            if status:
                logger.info("✓ Status obtido com sucesso")
                
                # Extrai informações relevantes
                network = status.get('node_info', {}).get('network')
                height = status.get('sync_info', {}).get('latest_block_height')
                catching_up = status.get('sync_info', {}).get('catching_up')
                
                logger.info(f"Network: {network}")
                logger.info(f"Block Height: {height}")
                logger.info(f"Node Syncing: {catching_up}")
                
                logger.debug(f"Status completo: {json.dumps(status, indent=2)}")
            else:
                logger.error("✗ Falha ao obter status do node")
            
            # 2. Teste de Informações ABCI
            logger.info("\n=== 2. Testando informações ABCI ===")
            abci_info = await client.get_latest_block()
            if abci_info:
                logger.info("✓ Informações ABCI obtidas com sucesso")
                
                # Extrai informações relevantes
                app_version = abci_info.get('response', {}).get('version')
                app_height = abci_info.get('response', {}).get('last_block_height')
                
                logger.info(f"App Version: {app_version}")
                logger.info(f"Last Block Height: {app_height}")
                
                logger.debug(f"ABCI Info: {json.dumps(abci_info, indent=2)}")
            else:
                logger.error("✗ Falha ao obter informações ABCI")
            
            # 3. Teste de Bloco Específico
            if height:
                logger.info(f"\n=== 3. Testando dados do bloco {height} ===")
                block = await client.get_block(int(height))
                if block:
                    logger.info("✓ Dados do bloco obtidos com sucesso")
                    
                    # Extrai informações relevantes
                    block_time = block.get('block', {}).get('header', {}).get('time')
                    num_txs = len(block.get('block', {}).get('data', {}).get('txs', []))
                    
                    logger.info(f"Block Time: {block_time}")
                    logger.info(f"Number of Transactions: {num_txs}")
                    
                    logger.debug(f"Block Data: {json.dumps(block, indent=2)}")
                else:
                    logger.error("✗ Falha ao obter dados do bloco")
            
            # 4. Teste de Dados de Mercado
            logger.info("\n=== 4. Testando dados de mercado ===")
            market_data = await client.get_market_data("ETH-USD")
            if market_data:
                logger.info("✓ Dados do mercado obtidos com sucesso")
                logger.debug(f"Market Data: {json.dumps(market_data, indent=2)}")
            else:
                logger.error("✗ Falha ao obter dados do mercado")
            
    except Exception as e:
        logger.error(f"Erro fatal durante os testes: {e}")
        raise

def main():
    """Função principal"""
    try:
        asyncio.run(test_node())
        logger.info("\n=== Testes concluídos! ===")
        
    except KeyboardInterrupt:
        logger.info("\n! Testes interrompidos pelo usuário")
    except Exception as e:
        logger.error(f"\n✗ Erro fatal: {e}")
    finally:
        logger.info("\nSessão de testes finalizada")

if __name__ == "__main__":
    main()