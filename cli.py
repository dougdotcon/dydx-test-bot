#!/usr/bin/env python3
"""
Interface de linha de comando para o bot de trading
"""

import click
import asyncio
import logging
from src.bot import TradingBot
from src.utils import load_config, setup_logging
import json
from pathlib import Path
import os

@click.group()
def cli():
    """Bot de Trading dYdX v4 - Estratégia de Breakout com Volume"""
    pass

@cli.command()
@click.option(
    '--market',
    default=None,
    help='Par de trading (ex: ETH-USD)'
)
@click.option(
    '--timeframe',
    default=None,
    help='Timeframe para análise (ex: 5m)'
)
@click.option(
    '--volume-factor',
    default=None,
    type=float,
    help='Fator multiplicador para detecção de volume anômalo'
)
@click.option(
    '--config',
    default='config/config.json',
    help='Caminho para arquivo de configuração'
)
def start(market, timeframe, volume_factor, config):
    """Inicia o bot de trading"""
    try:
        # Carrega configuração
        if not Path(config).exists():
            click.echo(f"Erro: Arquivo de configuração não encontrado: {config}")
            return
        
        # Configura logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Atualiza configurações com parâmetros da CLI
        if any([market, timeframe, volume_factor]):
            config_data = load_config()
            if market:
                config_data['trading']['market'] = market
            if timeframe:
                config_data['trading']['timeframe'] = timeframe
            if volume_factor:
                config_data['trading']['volume_factor'] = volume_factor
                
            # Salva configurações atualizadas
            with open(config, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
        
        click.echo("Iniciando bot de trading...")
        
        # Inicia o bot
        bot = TradingBot()
        asyncio.run(bot.start())
        
    except KeyboardInterrupt:
        click.echo("\nBot interrompido pelo usuário")
    except Exception as e:
        click.echo(f"Erro ao iniciar bot: {e}")
        raise

@cli.command()
@click.argument('market')
def status(market):
    """Verifica status do mercado específico"""
    try:
        bot = TradingBot()
        config = load_config()
        
        click.echo(f"\nStatus do Mercado: {market}")
        click.echo("-" * 40)
        
        # TODO: Implementar verificação de status
        # Será implementado junto com os módulos de execução
        click.echo("Funcionalidade em desenvolvimento")
        
    except Exception as e:
        click.echo(f"Erro ao verificar status: {e}")

@cli.command()
def version():
    """Mostra a versão do bot"""
    click.echo("dYdX Trading Bot v0.1.0")

@cli.command()
@click.option('--check', is_flag=True, help='Apenas verifica as configurações sem iniciar o bot')
def setup(check):
    """Configura ou verifica o ambiente do bot"""
    try:
        # Verifica arquivos necessários
        files_to_check = [
            ('config/config.json', 'Arquivo de configuração'),
            ('config/.env', 'Arquivo de variáveis de ambiente'),
            ('requirements.txt', 'Arquivo de dependências')
        ]
        
        click.echo("\nVerificando ambiente...")
        all_ok = True
        
        for file_path, description in files_to_check:
            exists = Path(file_path).exists()
            status = '✓' if exists else '✗'
            click.echo(f"{status} {description}: {file_path}")
            if not exists and file_path == 'config/.env':
                if Path('config/.env.example').exists():
                    click.echo("  → Copie .env.example para .env e configure suas credenciais")
                all_ok = False
        
        # Verifica variáveis de ambiente necessárias
        if Path('config/.env').exists():
            required_env = ['DYDX_TEST_MNEMONIC']
            missing_env = [env for env in required_env if not os.getenv(env)]
            if missing_env:
                all_ok = False
                click.echo("\nVariáveis de ambiente faltando:")
                for env in missing_env:
                    click.echo(f"✗ {env}")
        
        if check:
            if all_ok:
                click.echo("\nTodas as verificações passaram com sucesso!")
            else:
                click.echo("\nAlgumas verificações falharam. Corrija os problemas antes de iniciar o bot.")
            return
        
        # Se não for apenas verificação, continua com setup
        if not all_ok:
            if not click.confirm("\nDeseja continuar com o setup?", default=True):
                return
        
        click.echo("\nRealizando setup...")
        # TODO: Implementar passos adicionais de setup
        # (será expandido conforme necessidade)
        
    except Exception as e:
        click.echo(f"Erro durante setup: {e}")

if __name__ == '__main__':
    cli()