# magma-var
Python package for MAGMA Volcanic Activity Report (VAR)

# 1. How to use
Make sure you have MAGMA token. Check [examples directory](https://github.com/martanto/magma-var/tree/main/examples).

Volcano name and code:

| Volcano            | Code    |
|--------------------| ------- |
| Agung              | AGU     |
| Ambang             | AMB     |
| Anak Krakatau      | KRA     |
| Anak Ranakah       | RAN     |
| Arjuno Welirang    | WEL     |
| Awu                | AWU     |
| Banda Api          | BAN     |
| Batur              | BAT     |
| Batutara           | TAR     |
| Bromo              | BRO     |
| Bur Ni Telong      | TEL     |
| Ciremai            | CER     |
| Colo               | COL     |
| Dempo              | DEM     |
| Dieng              | DIE     |
| Dukono             | DUK     |
| Ebulobo            | EBU     |
| Egon               | EGO     |
| Galunggung         | GAL     |
| Gamalama           | GML     |
| Gamkonora          | GMK     |
| Gede               | GED     |
| Guntur             | GUN     |
| Ibu                | IBU     |
| Ijen               | IJE     |
| Ile Werung         | WER     |
| Ili Boleng         | BOL     |
| Ili Lewotolok      | LEW     |
| Inielika           | LIK     |
| Inierie            | RIE     |
| Iya                | IYA     |
| Kaba               | KAB     |
| Karangetang        | KAR     |
| Kelimutu           | KLM     |
| Kelud              | KLD     |
| Kerinci            | KER     |
| Kie Besi           | KIE     |
| Lamongan           | LAM     |
| Lereboleng         | LER     |
| Lewotobi Laki-laki | LWK     |
| Lewotobi Perempuan | LWP     |
| Lokon              | LOK     |
| Mahawu             | MAH     |
| Marapi             | MAR     |
| Merapi             | MER     |
| Papandayan         | PAP     |
| Peut Sague         | PEU     |
| Raung              | RAU     |
| Rinjani            | RIN     |
| Rokatenda          | ROK     |
| Ruang              | RUA     |
| Salak              | SAL     |
| Sangeangapi        | SAN     |
| Semeru             | SMR     |
| Seulawah Agam      | SEU     |
| Sinabung           | SIN     |
| Sirung             | SIR     |
| Slamet             | SLA     |
| Soputan            | SOP     |
| Sorikmarapi        | SOR     |
| Sumbing            | SBG     |
| Sundoro            | SUN     |
| Talang             | TAL     |
| Tambora            | TAM     |
| Tandikat           | TAN     |
| Tangkoko           | TGK     |
| Tangkuban Parahu   | TPR     |
| Teon               | TEO     |
| Wurlali            | WUR     |


## 1.1 Install module
```pip
pip install magma-var
```

Check your version:
```python
print(magma_var.__version__)
```

## 1.2 Download Volcanic Activity Report (VAR)
To download Volcanic Activity Report (VAR):


```python
import magma_var
from magma_auth import auth
from magma_var import Download
```


```python
print(magma_var.__version__)
```


```python
token = auth.token
```


```python
download = Download(
    token=token,
    volcano_code='LOK',
    start_date='2025-01-01',
    end_date='2025-06-08',
    locale="id", # [testing] Change to "en" for english translation 
    current_dir='D:\\Projects\\magma-var', # Change your current directory. Default to None.
    verbose=True,
)
```


```python
download.var()
```


```python
download.to_excel()
```


```python
download.to_csv()
```


## 1.3 Plot VAR
Plot seismicity count:

Earthquake name and code:

| Jenis Gempa         | Earthquake (EN)                      | Code |
|---------------------|--------------------------------------|------|
| Semua Gempa         | _Select all earthquake_              | *    |
| Letusan             | _Eruption_                           | lts  |
| Awan Panas Letusan  | _Fountain Collapse Pyroclastic Flow_ | apl  |
| Awan Panas Guguran  | _Pyroclastic Density Current (PDC)_  | apg  |
| Guguran             | _Rockfall_                           | gug  |
| Hembusan            | _Degassing_                          | hbs  |
| Harmonik            | _Harmonic_                           | hrm  |
| Tremor Non-Harmonik | _Non-Harmonic Tremor_                | tre  |
| Tornillo            | _Tornillo_                           | tor  |
| Low Frequency       | _Low Frequency_                      | lof  |
| Hybrid/Fase Banyak  | _Hybrid/Multi Phase_                 | hyb  |
| Vulkanik Dangkal    | _Shallow Volcanic-Tectonic (VT-B)_   | vtb  |
| Vulkanik Dalam      | _Deep Volcanic-Tectonic (VT-A)_      | vta  |
| Very Long Period    | _Very Long Period_                   | vlp  |
| Tektonik Lokal      | _Local Tectonic_                     | tel  |
| Terasa              | _Felt Earthquake_                    | trs  |
| Tektonik Jauh       | _Teleseismic_                        | tej  |
| Double Event        | _Double Event_                       | dev  |
| Getaran Banjir      | _Lahar_                              | gtb  |
| Deep Tremor         | _Deep Tremor_                        | dpt  |
| Tremor Menerus      | _Tremor_                             | mtr  |


```python
from magma_auth import auth
from magma_var import Plot
```


```python
token = auth.token
```


```python
plot = Plot(
    token = token,
    volcano_code = 'LOK',
    start_date = '2025-01-01',
    end_date = '2025-03-13',
    earthquake_code = '*', # Check table above for earthquake code
    locale = 'en',
    overwrite=True, # Overwrite existsing downloaded file
    verbose=True, # Show detailed information
)
```

Print DataFrame:
```python
plot.df
```

Show plot:
```python
plot.show(
    interval=7, # 7 days. X-axis interval in days. 
    width=1.0, # Size bar width
    title='Lokon', # Plot title
    figsize=(10,1),
    title_fontsize=12,
    figure_ylabel_fontsize=9,
    x_labelsize=8,
    y_labelsize=8,
    color='black',
)
```

# Changelog
## [0.0.11] 2025-07-22

Expecting breaking changes from previous version.

### Added

- Added english translation in `resources.py` for earthquakes type.
- Added `debug` property for developing purposes.

### Fixed

- Increase performance by caching some results.
- Fix inconsistent output directory.
- Fix felt earthquake not detected.

### Changed

- `load_token()` method will unpack 3 variables, `success (bool)`, `token (str)`, 
`expired_date (str)` instead of two variables `success (bool)` and `token (str)`.
- Code reformatting using `black`.
