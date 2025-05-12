"""
Módulo de utilidades e funções auxiliares para o bot
"""

import json
import logging
from pathlib import Path
from typing import Dict
import os
from dotenv import load_dotenv

def setup_logging(log_level: str = "INFO") -> None:
    """
    Configura o sistema de logging do bot
    
    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console
            logging.FileHandler(  # Arquivo
                filename=os.getenv("LOG_FILE", "bot.log"),
                encoding="utf-8"
            )
        ]
    )

def load_config() -> Dict:
    """
    Carrega as configurações do arquivo config.json
    
    Returns:
        Dict com as configurações
    """
    try:
        config_path = Path("config/config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise Exception(f"Erro ao carregar config.json: {e}")

def load_env() -> None:
    """
    Carrega variáveis de ambiente do arquivo .env
    """
    env_path = Path("config/.env")
    if not env_path.exists():
        raise Exception(
            "Arquivo .env não encontrado. "
            "Copie .env.example para .env e configure suas credenciais."
        )
    load_dotenv(env_path)

def validate_config(config: Dict) -> None:
    """
    Valida as configurações carregadas
    
    Args:
        config: Dict com as configurações
    
    Raises:
        Exception: Se alguma configuração obrigatória estiver faltando
    """
    required_keys = {
        "trading": ["market", "timeframe", "volume_factor", "risk_reward_ratio"],
        "risk": ["max_position_size", "max_risk_per_trade"],
        "technical": ["resistance_period", "volume_lookback"],
        "network": {
            "endpoints": ["grpc", "rest"]
        }
    }

    def check_keys(data: Dict, keys: Dict, path: str = ""):
        for key, value in keys.items():
            if key not in data:
                raise Exception(f"Configuração obrigatória faltando: {path}{key}")
            if isinstance(value, list):
                for subkey in value:
                    if subkey not in data[key]:
                        raise Exception(
                            f"Configuração obrigatória faltando: {path}{key}.{subkey}"
                        )
            elif isinstance(value, dict):
                check_keys(data[key], value, f"{path}{key}.")

    check_keys(config, required_keys)

def format_price(price: float, decimals: int = 2) -> str:
    """
    Formata um preço para exibição
    
    Args:
        price: Preço a ser formatado
        decimals: Número de casas decimais
    
    Returns:
        String formatada do preço
    """
    return f"{price:.{decimals}f}"

def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calcula o tamanho da posição baseado no risco
    
    Args:
        account_balance: Saldo da conta
        risk_per_trade: Percentual de risco por operação (0.02 = 2%)
        entry_price: Preço de entrada
        stop_loss: Preço do stop loss
    
    Returns:
        Tamanho da posição em unidades do ativo
    """
    risk_amount = account_balance * risk_per_trade
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        raise ValueError("Preço de entrada igual ao stop loss")
    
    position_size = risk_amount / price_risk
    return position_size