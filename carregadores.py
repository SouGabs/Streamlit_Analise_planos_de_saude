"""Carregadores dos arquivos CSV utilizados pela aplicação Streamlit."""

from pathlib import Path

import pandas as pd


class CarregadorCSV:
    """Classe base para leitura dos CSVs do projeto."""

    nome_arquivo: str

    def __init__(self, diretorio: str | Path | None = None) -> None:
        projeto = Path(__file__).parent
        self.diretorio = Path(diretorio) if diretorio else projeto / "dados"

    @property
    def caminho_arquivo(self) -> Path:
        return self.diretorio / self.nome_arquivo

    def carregar(self) -> pd.DataFrame:
        """Lê o arquivo CSV e devolve seu conteúdo em um DataFrame."""
        return pd.read_csv(
            self.caminho_arquivo,
            sep=";",
            # Os arquivos de origem estão codificados em ISO-8859-1 (Latin-1).
            encoding="latin1",
            dtype=str,
        )

class CarregadorAcidentes(CarregadorCSV):
    nome_arquivo = "Acidentes.csv"


class CarregadorMunicipios(CarregadorCSV):
    nome_arquivo = "municipios.csv"


class CarregadorCadopCanceladas(CarregadorCSV):
    nome_arquivo = "Relatorio_cadop_canceladas.csv"


class CarregadorEmpresasPlanoSaude(CarregadorCSV):
    nome_arquivo = "Relatorio_cadop_empresas_de_plano_saude.csv"


def carregar_dataframes(
    diretorio: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Retorna municípios, canceladas, ativas e acidentes, nesta ordem."""
    municipios = CarregadorMunicipios(diretorio).carregar()
    cadop_canceladas = CarregadorCadopCanceladas(diretorio).carregar()
    empresas_plano_saude = CarregadorEmpresasPlanoSaude(diretorio).carregar()
    acidentes = CarregadorAcidentes(diretorio).carregar()

    return municipios, cadop_canceladas, empresas_plano_saude, acidentes
