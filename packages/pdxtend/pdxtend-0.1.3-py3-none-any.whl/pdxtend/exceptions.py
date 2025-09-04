# pdxtend/exceptions.py

class PdxtendError(Exception):
    """
        Exceção base para todos os erros específicos da biblioteca pdxtend.

        Isso permite que os usuários capturem qualquer erro gerado pela nossa
        biblioteca com um único 'except PdxtendError:'.
    """
    pass

class ConfigError(PdxtendError):
    """
        Relacionado a erros no arquivo de configuração (config.json).
        Ex: arquivo não encontrado, JSON mal formatado.
    """
    pass

class FileProcessingError(PdxtendError):
    """
        Relacionado a erros ao ler ou validar um arquivo (Excel, etc.).
        Ex: arquivo corrompido, formato não suportado.
    """
    pass

class InvalidSheetError(PdxtendError):
    """
        Erro específico para quando uma planilha (sheet) não é encontrada.
        Note que ela herda de FileProcessingError, criando uma hierarquia.
    """
    pass

class SavingError(PdxtendError):
    """
        Erro específico para quando não consegue salvar algum arquivo
    """
    pass