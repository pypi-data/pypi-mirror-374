import pandas as pd
import os
import json
import logging
from typing import Optional, Union, Sequence, Dict
from .exceptions import PdxtendError, ConfigError, FileProcessingError, InvalidSheetError, SavingError

log = logging.getLogger(__name__)


class ExcelReader:
    """
    A utility class for loading, updating, and saving Excel files using pandas.
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        """
        Initialize the ExcelReader and load config if available.

        Parameters
        ----------
        config_file : str, default 'config.json'
            Path to the config JSON file containing the Excel path and sheet.
        """
        self._data: Dict[str, pd.DataFrame] = {}
        self._path: Optional[str] = None
        self._sheet: Optional[str] = None
        self.config_file = config_file

        if not os.path.exists(self.config_file):
            try:
                self._load_config()
            except ConfigError as e:
                log.warning(f"Não foi possível carregar a configuração: {e}")

    @property
    def data(self) -> Dict[str, pd.DataFrame]:
        """
        Returns the loaded DataFrames, loading them if necessary.

        Returns
        -------
        Dict[str, pd.DataFrame]
        """
        if not self._data:
            raise PdxtendError(f'Nenhum dado foi carregado. Chame o método "load_file()" primeiro.')
        return self._data

    def _load_config(self) -> None:
        """
        Lê o arquivo de configuração e carrega os arquivos especificados.
        """
        log.info(f"Carregando configuração de \'{self.config_file}\'...")
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    log.info(f"Arquivo de configuração \'{self.config_file}\' está vazio")
                    return

                config = json.loads(content)
                if "loaded_files" in config:
                    # Carrega todos os arquivos listados na configuração
                    self.load_file(config["loaded_files"])
                else:
                    # Mantém a compatibilidade com a configuração antiga, se necessário
                    self._path = config.get("path")
                    self._sheet = config.get("sheet")

        except json.JSONDecodeError as e:
            raise ConfigError(f"O arquivo de configuração \'{self.config_file}\' está mal formatado.") from e
        except Exception as e:
            raise ConfigError(f"Erro inesperado ao carregar a configuração: {e}") from e

    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        Salva a configuração de arquivos carregados no arquivo de configuração.

        Parameters
        ----------
        file_path : str, optional
            O caminho do arquivo específico cuja configuração deve ser salva.
            Se None, a configuração de todos os arquivos carregados será salva.
        """
        config_to_save = []
        if file_path:
            if file_path in self._data:
                # Assumindo que você pode querer salvar o nome da planilha também.
                # Se o nome da planilha não for armazenado no DataFrame, você precisará
                # encontrar uma maneira de associá-lo ao caminho.
                # Por simplicidade, vamos usar o caminho como identificador único.
                # Se você precisar do nome da planilha, considere armazená-lo
                # como um atributo do DataFrame ou passá-lo junto com o path.
                config_to_save.append({"path": file_path, "sheet": ""})  # Placeholder para sheet
            else:
                log.warning(
                    f"Arquivo \'{file_path}\' não encontrado entre os dados carregados. Nenhuma configuração salva para este arquivo.")
                return
        else:
            for path, df in self._data.items():
                config_to_save.append({"path": path, "sheet": ""})  # Placeholder para sheet

        config = {"loaded_files": config_to_save}
        log.info(f"Salvando configuração em \'{self.config_file}\' : {config}")
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            log.info("Configuração salva com sucesso.")
        except Exception as e:
            raise ConfigError(f"Falha ao salvar o arquivo de configuração em \'{self.config_file}\' : {e}") from e

    def load_file(self, files_to_load: Union[Dict[str, str], Sequence[Dict[str, str]]]) -> Dict[str, pd.DataFrame]:
        """
        Carrega um ou mais arquivos Excel a partir de caminhos e nomes de planilhas.

        Parameters
        ----------
        files_to_load : Union[Dict[str, str], Sequence[Dict[str, str]]]
            Pode ser um dicionário único com 'path' e 'sheet', ou uma lista de dicionários,
            onde cada dicionário contém 'path' e 'sheet' para um arquivo.

        Returns
        -------
        Dict[str, pd.DataFrame]
            Um dicionário onde as chaves são os caminhos dos arquivos e os valores são os DataFrames carregados.

        Raises
        ------
        ConfigError
            Se o caminho ou a planilha não forem fornecidos ou estiverem mal formatados.
        FileProcessingError
            Se o arquivo não for encontrado ou houver um erro ao lê-lo.
        InvalidSheetError
            Se a planilha especificada não existir no arquivo.
        """
        if isinstance(files_to_load, dict):
            files_to_load = [files_to_load]  # Converte para lista para processamento unificado

        loaded_data = {}
        for file_config in files_to_load:
            current_path = file_config.get('path')
            current_sheet = file_config.get('sheet')

            if not current_path:
                raise ConfigError("O caminho do arquivo (path) não foi fornecido para um dos arquivos.")
            if not current_sheet:
                raise ConfigError("O nome da planilha (sheet) não foi fornecido para um dos arquivos.")

            try:
                log.info(f"Carregando arquivo: \'{current_path}\' | Planilha: \'{current_sheet}\'")

                xls = pd.ExcelFile(current_path)

                if current_sheet not in xls.sheet_names:
                    raise InvalidSheetError(
                        f"A planilha \'{current_sheet}\' não existe em \'{current_path}\'. "
                        f"Planilhas disponíveis: {xls.sheet_names}"
                    )

                df = pd.read_excel(xls, sheet_name=current_sheet)
                df.attrs["original_sheet_name"] = current_sheet # Adicionado para Opção 1 de sheet_name
                loaded_data[current_path] = df
                log.info(f"Arquivo \'{current_path}\' carregado e dados armazenados com sucesso.")

            except FileNotFoundError as e:
                log.error(f"Arquivo não encontrado: \'{current_path}\'. Erro: {e}")
                raise FileProcessingError(f"Arquivo não encontrado no caminho: \'{current_path}\'")
            except InvalidSheetError as e:
                log.error(f"Planilha inválida para \'{current_path}\'. Erro: {e}")
                raise
            except Exception as e:
                log.error(f"Falha ao processar o arquivo \'{current_path}\'. Erro: {e}")
                raise FileProcessingError(f"Falha ao processar o arquivo \'{current_path}\' : {e}") from e

        self._data.update(loaded_data)
        return self._data

    def save_data(self, file_paths: Optional[Union[str, Sequence[str]]] = None, **kwargs) -> None:
        """
        Salva um ou mais DataFrames em arquivos Excel.

        Parameters
        ----------
        file_paths : Optional[Union[str, Sequence[str]]]
            Um único caminho de arquivo (str) ou uma lista de caminhos de arquivos (Sequence[str])
            a serem salvos. Se None, todos os DataFrames carregados na instância serão salvos.
            Os DataFrames devem estar presentes no `self._data`.
        **kwargs
            Argumentos adicionais a serem passados para `pandas.DataFrame.to_excel`
            (ex: index=False, float_format="%.2f").
        """
        if file_paths is None:
            # Salvar todos os DataFrames carregados
            files_to_save = list(self._data.keys())
        elif isinstance(file_paths, str):
            # Salvar um único DataFrame especificado
            files_to_save = [file_paths]
        else:
            # Salvar múltiplos DataFrames especificados
            files_to_save = file_paths

        if not files_to_save:
            log.warning(
                "Nenhum arquivo para salvar. Verifique se há DataFrames carregados ou se os caminhos especificados são válidos.")
            return

        for path in files_to_save:
            if path not in self._data:
                log.warning(f"O arquivo \'{path}\' não está carregado na instância. Pulando o salvamento.")
                continue

            dataframe = self._data[path]
            # Tenta obter o nome da planilha original, caso contrário, usa 'Sheet1'
            sheet_name = dataframe.attrs.get("original_sheet_name", "Sheet1") # Modificado para Opção 1

            log.info(f"Salvando dados em \'{path}\' (planilha: {sheet_name})...")
            try:
                dataframe.to_excel(path, sheet_name=sheet_name, **kwargs)
                log.info(f"Dados salvos com sucesso em \'{path}\'")
            except Exception as e:
                log.error(f"Falha ao salvar o arquivo em \'{path}\' : {e}")
                raise SavingError(f"Falha ao salvar o arquivo em \'{path}\' : {e}") from e

    def save_dataframes_to_single_excel(self, file_path: str, dataframes_to_save: Dict[str, pd.DataFrame], **kwargs) -> None:
        """
        Salva múltiplos DataFrames em um único arquivo Excel, cada um em uma planilha diferente.

        Parameters
        ----------
        file_path : str
            O caminho completo do arquivo Excel de destino (ex: "caminho/para/seu/relatorio_final.xlsx").
        dataframes_to_save : Dict[str, pd.DataFrame]
            Um dicionário onde as chaves são os nomes das planilhas e os valores são os DataFrames
            a serem salvos em cada planilha.
        **kwargs
            Argumentos adicionais a serem passados para `pandas.ExcelWriter` (ex: engine='xlsxwriter')
            e para `pandas.DataFrame.to_excel` (ex: index=False, float_format="%.2f").
        """
        log.info(f"Salvando múltiplos DataFrames em um único arquivo Excel: \'{file_path}\'...")
        try:
            with pd.ExcelWriter(file_path, **kwargs) as writer:
                for sheet_name, dataframe in dataframes_to_save.items():
                    log.info(f"Escrevendo planilha: \'{sheet_name}\'...")
                    dataframe.to_excel(writer, sheet_name=sheet_name, **kwargs)
            log.info(f"Todos os DataFrames salvos com sucesso em \'{file_path}\'")
        except Exception as e:
            raise SavingError(f"Falha ao salvar múltiplos DataFrames no arquivo \'{file_path}\' : {e}") from e