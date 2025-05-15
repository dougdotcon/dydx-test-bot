"""
Script para testar a conexão com RPC nodes da dYdX v4
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
    # URLs de RPC nodes públicos da dYdX v4
    urls = [
        "https://dydx-testnet-archive.allthatnode.com:26657",
        "https://dydx.testnet.node.blockapex.io",
        "https://dydx-testnet-full.allthatnode.com:26657",
        "https://dydx-testnet-rpc.polkachu.com",
        "https://dydx-testnet.rpc.bccnodes.com"
    ]
    
    # Endpoints a testar em cada node
    endpoints = [
        "/status",  # Status do node
        "/abci_info",  # Informações básicas
        "/net_info"  # Informações de rede
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
        headers={'Accept': 'application/json'}
    ) as session:
        for base_url in urls:
            logger.info(f"\nTestando RPC node: {base_url}")
            
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    logger.info(f"\nTestando endpoint: {url}")
                    async with session.get(url) as response:
                        logger.info(f"Status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Resposta: {json.dumps(data, indent=2)}")
                            
                            # Se conseguimos conectar com sucesso, vamos salvar estas informações
                            if 'result' in data:
                                with open('working_node.json', 'w') as f:
                                    json.dump({
                                        'url': base_url,
                                        'status': 'working',
                                        'last_response': data
                                    }, f, indent=2)
                                logger.info(f"Node funcional encontrado: {base_url}")
                                
                        else:
                            text = await response.text()
                            logger.error(f"Erro: {text}")
                except Exception as e:
                    logger.error(f"Erro ao conectar em {url}: {str(e)}")
                
                await asyncio.sleep(1)

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