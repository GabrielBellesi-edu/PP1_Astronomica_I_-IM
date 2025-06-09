# Practica Profesionalizante 1 - Calculo del Indice de Masa

[![GitHub](https://img.shields.io/badge/GitHub-Proyecto-181717?logo=github)](https://github.com/GabrielBellesi-edu/PP1_Astronomica_I_-IM)
[![Trello](https://img.shields.io/badge/Trello-Board-0052CC?logo=trello)](https://trello.com/b/NkFtRkHn/equipo-pp1-astronomica-i-im)
[![Google Drive](https://img.shields.io/badge/Google%20Drive-Carpeta%20de%20Trabajo-34A853?logo=google-drive)](https://drive.google.com/drive/folders/1s82XNqycWEkGKi1vTNnPkHEaIjf30QIh)
[![Cookiecutter](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?logo=matplotlib)](https://matplotlib.org/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly)](https://plotly.com/)
[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=power-bi)](https://powerbi.microsoft.com/)




Repositorio del proyecto Astronomica I (IM), de la materia Practica Profesionalizante I


## 👥 Autores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/GabrielBellesi-edu">
        <img src="https://github.com/GabrielBellesi-edu.png" width="100px;" alt="Gabriel" />
        <br /><sub><b>Bellesi Gabriel</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Gise08">
        <img src="https://github.com/Gise08.png" width="100px;" alt="Gisela" />
        <br /><sub><b>García Gisela</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Criiistiiian">
        <img src="https://github.com/Criiistiiian.png" width="100px;" alt="Cristian" />
        <br /><sub><b>Ortiz Cristian</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/vanrios5">
        <img src="https://github.com/vanrios5.png" width="100px;" alt="Vanesa" />
        <br /><sub><b>Ríos Vanesa</b></sub>
      </a>
    </td>
  </tr>
</table>





## Project Organization

```
├── LICENSE                     <- EMPTY / Open-source license
├── .gitattributes              <- NEW / Configuracion de archivos tratados con Git LFS
├── .gitignore                  <- NEW / Ignora los archivos y carpetas seleccionadas
├── Makefile                    <- EMPTY / Makefile with convenience commands like `make data` or `make train`
├── README.md                   <- DOING / The top-level README for developers using this project.
├── data
│   ├── external                <- EMPTY / Data from third party sources.
│   ├── interim                 <- DONE / Intermediate data that has been transformed.
│   ├── processed               <- DONE / The final, canonical data sets for modeling.
│   └── raw                     <- DONE / The original, immutable data dump.
│
├── docs                        <- EMPTY / A default mkdocs project; see www.mkdocs.org for details
│
├── models                      <- EMPTY / Trained and serialized models, model predictions, or model summaries
│
├── notebooks                   <- DOING / Jupyter notebooks. 
│   ├── 1.0-PP1-IM-limpieza-dataset.ipynb   <- NEW / Notebook con limpieza del DataSet
│   └── 2.0-PP1-IM-calculo-indice.ipynb     <- NEW / notebook con el calculo del indice de masa
│
├── pyproject.toml              <- EMPTY / Project configuration file with package metadata for 
│                               calculo and configuration for tools like black
│
├── references                  <- DOING / Data dictionaries, manuals, and all other explanatory materials.
│
│
├── reports                     <- DOING / Generated analysis as HTML, PDF, LaTeX, etc.
│   ├── CalculoDiario/          <- NEW / REPORTE DIARIO
│   ├── CalculoSemanal/         <- NEW / REPORTE SEMANAL
│   ├── CalculoMensual/         <- NEW / REPORTE MENSUAL
│   ├── CalculoTrimestral/      <- NEW / REPORTE TRIMESTRAL
│   ├── CalculoCuatrimestral/   <- NEW / REPORTE CUATRIMESTRAL
│   ├── CalculoSemestral/       <- NEW / REPORTE SEMESTRAL
│   ├── CalculoAnual/           <- NEW / REPORTE ANUAL
│   └── 2024_consolidado_IM_temporalidades.csv  <- NEW / Resultados del calculo de indice de masa. 
│                                                 Tabla 2 para PowerBi
│
├── requirements.txt            <- CHECK / The requirements file for reproducing the analysis environment, e.g.
│                               generated with `pip freeze > requirements.txt`
│
├── setup.cfg                   <- EMPTY / Configuration file for flake8
│
│
└── src/                        <- NEW / ESPACIO PARA EL CODIGO
    │
    ├── calculo/                <- NEW / ESPACIO PARA EL CODIGO DEDICADO A LA LIMPIEZA DEL DATASET
    │   ├── __init__.py         <- NEW / Makes calculo a Python module
    │   ├── informe_indice_masa.py  <- NEW / Realiza los reportes temporales.TXT 
    │   └── tabla_indice_masa.py    <- NEW / Realiza los calculos para el indice de masa
    │                               Crea el archivo 2024_consolidado_IM_temporalidades.csv
    │
    └── limpieza/               <- NEW / ESPACIO PARA EL CODIGO DEDICADO AL CALCULO DEL IM
        ├── __init__.py         <- NEW / Makes calculo a Python module
        ├── data_cleaning.py    <- NEW / Ejecuta el programa para la conversion, limpieza y transformacion del DataSet
        ├── filtrado_extras_rge_inferior.py   <- NEW / Programa adicional para filtrar resultados sobre el rango establecido
        ├── filtrado_extras_rge_superior.py   <- NEW / Programa adicional para filtrar resultados debajo del rango establecido
        └── solo_amax.py        <- NEW / Programa que elimina todos los datos del Dataset, salvo el valor de amax (optimizar rendimiento en etapa de testos)

```

pip install --user git-filter-repo


--------

