"""
Script para testar a conexão WebSocket com a dYdX
"""
import asyncio
import websockets
import json
import logging
import ssl
import certifi

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_websocket():
    # URLs do WebSocket para testar
    ws_urls = [
        "wss://indexer.v4-testnet.dydx.exchange/v4/ws",
        "wss://indexer.dydx.exchange/v4/ws"
    ]
    
    # Mensagem de subscrição
    subscribe_msg = {
        "type": "subscribe",
        "channel": "v4_markets",
        "id": "ETH-USD"
    }
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for ws_url in ws_urls:
        try:
            logger.info(f"\nTentando conectar ao WebSocket: {ws_url}")
            
            async with websockets.connect(
                ws_url,
                ssl=ssl_context,
                ping_interval=None,
                close_timeout=5
            ) as websocket:
                logger.info("Conexão estabelecida!")
                
                # Envia mensagem de subscrição
                await websocket.send(json.dumps(subscribe_msg))
                logger.info(f"Enviada mensagem de subscrição: {subscribe_msg}")
                
                # Aguarda e processa mensagens por 30 segundos
                try:
                    for _ in range(5):  # Tenta receber 5 mensagens
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        logger.info(f"Recebido: {json.dumps(data, indent=2)}")
                except asyncio.TimeoutError:
                    logger.warning("Timeout aguardando mensagens")
                
        except Exception as e:
            logger.error(f"Erro na conexão WebSocket: {str(e)}")
        
        await asyncio.sleep(2)  # Pausa entre tentativas

def main():
    """Função principal"""
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        logger.info("\nTeste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        logger.info("\nTeste finalizado")

if __name__ == "__main__":
    main()