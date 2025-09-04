import logging
import sys
from typing import Optional, Dict, Any
from aigency.utils.singleton import Singleton


class Logger(Singleton):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if hasattr(self, '_initialized'):
            # Si ya está inicializado y se pasa nueva config, actualizar
            if config and config != getattr(self, 'config', {}):
                self.config.update(config)
                self._setup_logger()
            return
        
        self._initialized = True
        self.config = config or {}
        self._logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger con la configuración proporcionada"""
        # Obtener configuración del logger
        log_level = self.config.get('log_level', 'INFO').upper()
        log_format = self.config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = self.config.get('log_file')
        logger_name = self.config.get('logger_name', 'aigency')
        
        # Crear logger
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Evitar duplicar handlers si ya existen
        if self._logger.handlers:
            return
        
        # Crear formatter
        formatter = logging.Formatter(log_format)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # Handler para archivo si se especifica
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log a debug message"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log an info message"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log a warning message"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log an error message"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log a critical message"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log an exception with traceback"""
        self._logger.exception(message, *args, **kwargs)
    
    def set_level(self, level: str):
        """Cambiar el nivel de logging dinámicamente"""
        log_level = level.upper()
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        for handler in self._logger.handlers:
            handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    def get_logger(self):
        """Obtener la instancia del logger interno"""
        return self._logger


# Función de conveniencia para obtener la instancia del logger
def get_logger(config: Optional[Dict[str, Any]] = None) -> Logger:
    """
    Obtiene la instancia singleton del logger.
    Si es la primera vez que se llama y se proporciona config, se usa esa configuración.
    
    Args:
        config: Configuración opcional para el logger (solo se usa en la primera llamada)
    
    Returns:
        Instancia singleton del Logger
    """
    return Logger(config)