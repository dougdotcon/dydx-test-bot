"""
Script para testar a conexão com a API da dYdX
"""
import asyncio
import aiohttp
import logging
import ssl
import certifi
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_connection():
    # URLs para testar (baseadas na documentação mais recente da dYdX v4)
    urls = [
        "https://indexer.v4-testnet.dydx.exchange/v4/orderbooks/ETH-USD",
        "https://indexer.v4-testnet.dydx.exchange/v4/markets",
        "https://api.dydx.exchange/v4/trades/ETH-USD",
        "https://indexer.dydx.exchange/v4/markets",
        "https://api.dydx.exchange/v4/active-orders",
        # URLs alternativas
        "https://dydx-testnet.node.fprmxm.org/v4/markets",
        "https://dydx-testnet.kingnodes.com/v4/markets"
    ]
    
    # Configuração SSL
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Configura a sessão HTTP
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        force_close=True,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    ) as session:
        for url in urls:
            try:
                logger.info(f"\nTestando URL: {url}")
                async with session.get(url) as response:
                    logger.info(f"Status: {response.status}")
                    logger.info(f"Headers: {response.headers}")
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Resposta: {json.dumps(data, indent=2)}")
                    else:
                        text = await response.text()
                        logger.error(f"Erro: {text}")
            except Exception as e:
                logger.error(f"Erro ao conectar em {url}: {str(e)}")
            
            await asyncio.sleep(2)  # Pausa entre requisições

def main():
    """Função principal"""
    try:
        asyncio.run(test_connection())
    except KeyboardInterrupt:
        logger.info("\nTeste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        logger.info("\nTeste finalizado")

if __name__ == "__main__":
    main()