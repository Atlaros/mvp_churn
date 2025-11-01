"""
Configuración centralizada de logging para el sistema
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Configuración
LOG_DIR = 'logs'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Crear directorio de logs si no existe
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, log_file=None, level=None):
    """
    Configura y retorna un logger
    
    Args:
        name: Nombre del logger (usualmente __name__)
        log_file: Nombre del archivo de log (opcional)
        level: Nivel de logging (opcional)
    
    Returns:
        Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)
    
    # Establecer nivel
    if level is None:
        level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (si se especifica)
    if log_file:
        file_path = os.path.join(LOG_DIR, log_file)
        
        # Rotating File Handler (10MB, 5 backups)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name):
    """
    Obtiene un logger configurado
    
    Args:
        name: Nombre del módulo
    
    Returns:
        Logger configurado
    """
    # Determinar archivo de log basado en el módulo
    if 'app' in name:
        log_file = f'streamlit_{datetime.now().strftime("%Y%m%d")}.log'
    elif 'api' in name:
        log_file = f'api_{datetime.now().strftime("%Y%m%d")}.log'
    elif 'train' in name:
        log_file = f'training_{datetime.now().strftime("%Y%m%d")}.log'
    else:
        log_file = f'general_{datetime.now().strftime("%Y%m%d")}.log'
    
    return setup_logger(name, log_file)

# Logger por defecto
default_logger = setup_logger('churn_prediction', 'application.log')

# Función de conveniencia para logging rápido
def log_event(message, level='info', logger_name='churn_prediction'):
    """
    Log rápido de eventos
    
    Args:
        message: Mensaje a loggear
        level: Nivel (info, warning, error, debug)
        logger_name: Nombre del logger
    """
    logger = logging.getLogger(logger_name)
    
    level_map = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }
    
    log_func = level_map.get(level.lower(), logger.info)
    log_func(message)

# Ejemplos de uso
if __name__ == "__main__":
    # Logger básico
    logger = get_logger(__name__)
    
    logger.debug("Mensaje de debug")
    logger.info("Mensaje informativo")
    logger.warning("Mensaje de advertencia")
    logger.error("Mensaje de error")
    logger.critical("Mensaje crítico")
    
    # Log rápido
    log_event("Evento registrado", "info")
    log_event("Algo salió mal", "error")
    
    print(f"\n✅ Logs guardados en: {LOG_DIR}/")
    print(f"   - application.log")
    print(f"   - logging_config_{datetime.now().strftime('%Y%m%d')}.log")