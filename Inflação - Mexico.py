# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 17:44:16 2020

@author: rafael.lincoln
"""

import requests
import pandas as pd
from matplotlib.gridspec import GridSpec
import numpy as np

# =============================================================================
# Inflação
# =============================================================================

# Função p/ pegar time-series do INEGI

def time_series(codigo,token,periodo = 'mensal'):
    url = f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{codigo}/es/0700/false/BIE/2.0/{token}?type=json'
    content = requests.get(url) 
    # Retrieves data
    df = pd.DataFrame(content.json()['Series'][0]['OBSERVATIONS'])
    
    ts = df[['OBS_VALUE','TIME_PERIOD']]
    # tidying
    ts.OBS_VALUE = pd.to_numeric(ts.OBS_VALUE)
    
    if periodo == 'bi_weekly':
        ts.TIME_PERIOD = pd.to_datetime(ts.TIME_PERIOD).dt.to_period('D')
    elif periodo == 'quarter':
        ts['quarter'] = ts.TIME_PERIOD.str[5:].astype(int)
        ts['quarter'] = [x*3 for  x in ts.quarter]
        ts.TIME_PERIOD = ts.TIME_PERIOD.str[0:5] + ts.quarter.astype(str)
        ts.TIME_PERIOD = pd.to_datetime(ts.TIME_PERIOD).dt.to_period('Q')
        ts = ts.drop(['quarter'], axis = 1)
    else:
        ts.TIME_PERIOD = pd.to_datetime(ts.TIME_PERIOD).dt.to_period('M')
    
    ts = ts.rename(columns = {'TIME_PERIOD':'dates',
                              'OBS_VALUE':'values'})\
                    .set_index('dates', drop = True, inplace = False)
    return ts



# Link to the requested site: https://www.inegi.org.mx/servicios/api_indicadores.html

# Requested token, for unique use only
token = "98e4edd2-7117-b44e-f48b-8c370d1b0ca9"

############################# CPI ~ INPC (mexico) #############################


cpi = {'indice':{
        'total':'628194',
        'subjacente':{
                'total':'628195',
                'mercadorias':'628196',
                'servicos':'628197'},
        'nao_subjacente':{
                'total':'628198',
                'agropecuarios':'628199',
                'energia_e_administrados_gov':'628200'}},
        'MoM':{
            'total':'628201',
            'subjacente':{
                    'total':'628202',
                    'mercadorias':'628203',
                    'servicos':'628204'},
            'nao_subjacente':{
                    'total':'628205',
                    'agropecuarios':'628206',
                    'energia_e_administrados_gov':'628207'}},
        'a12':{
            'total':'628208',
            'subjacente':{
                    'total':'628209',
                    'mercadorias':'628210',
                    'servicos':'628211'},
            'nao_subjacente':{
                    'total':'628212',
                    'agropecuarios':'628213',
                    'energia_e_administrados_gov':'628214'}},
        'acumulada_ano':{
            'total':'628215',
            'subjacente':{
                    'total':'628216',
                    'mercadorias':'628217',
                    'servicos':'628218'},
            'nao_subjacente':{
                    'total':'628219',
                    'agropecuarios':'628220',
                    'energia_e_administrados_gov':'628221'}},
        'bi_weekly_indice':{
            'total':'628222',
            'subjacente':{
                    'total':'628223',
                    'mercadorias':'628224',
                    'servicos':'628225'},
            'nao_subjacente':{
                    'total':'628226',
                    'agropecuarios':'628227',
                    'energia_e_administrados_gov':'628228'}},
        'bi_weekly_mom':{
            'total':'628229',
            'subjacente':{
                    'total':'628230',
                    'mercadorias':'628231',
                    'servicos':'628232'},
            'nao_subjacente':{
                    'total':'628233',
                    'agropecuarios':'628234',
                    'energia_e_administrados_gov':'628235'}}}


for variable in cpi.keys():
    periodo = 'bi_weekly'
    if periodo in variable:
        arg = cpi[variable].keys()
        names = []
        for variable_2 in arg:
            if variable_2 == 'total':
                codigo = cpi[variable][variable_2]
                ts = time_series(codigo,token,periodo)
                # Renaming
                nome = 'cpi_'+variable +'_'+variable_2
                globals()[nome] = ts
                names.append(nome)
            else:
                kwarg = cpi[variable][variable_2].keys()
                for variable_3 in kwarg:
                    codigo = cpi[variable][variable_2][variable_3]
                    ts = time_series(codigo,token,periodo)
                    # Renaming
                    nome = 'cpi_'+variable+'_'+variable_2 + '_' + variable_3
                    globals()[nome] = ts
                    names.append(nome)
        # Global dataframes
        globals()['CPI_'+variable] = pd.concat([eval(name) for name in names], axis =1 )
        exec('CPI_' + variable + '.columns' + " = ['total','subjacente','mercadorias','serviços','nao_subjacente','agropecuaria','energeticos_e_tarifas']")

    else:
        arg = cpi[variable].keys()
        names = []
        for variable_2 in arg:
            if variable_2 == 'total':
                codigo = cpi[variable][variable_2]
                ts = time_series(codigo,token)
                # Renaming
                nome = 'cpi_'+variable +'_'+variable_2
                globals()[nome] = ts
                names.append(nome)
            else:
                kwarg = cpi[variable][variable_2].keys()
                for variable_3 in kwarg:
                    codigo = cpi[variable][variable_2][variable_3]
                    ts = time_series(codigo,token)
                    nome = 'cpi_'+variable+'_'+variable_2 + '_' + variable_3
                    globals()[nome] = ts
                    names.append(nome)
        # Global dataframes
        globals()['CPI_'+variable] = pd.concat([eval(name) for name in names], axis =1)
        exec('CPI_' + variable + '.columns' + " = ['total','subjacente','mercadorias','serviços','nao_subjacente','agropecuaria','energeticos_e_tarifas']")



# To SQL
        
for cpi in ['CPI_MoM','CPI_a12','CPI_acumulada_ano',\
            'CPI_bi_weekly_indice','CPI_bi_weekly_mom',\
            'CPI_indice']:
    exec(cpi + '.index = '+cpi+'.index.to_timestamp()')        
        
cpi_bi_weekly_mom['quinzena'] = np.where(cpi_bi_weekly_mom.index.day == 2, 'segunda quinzena','primeira quizena')
        
from sqlalchemy import create_engine

engine = create_engine('mysql://economistas:Mudar2019@@10.11.0.11/economia')

CPI_MoM.to_sql("cpi_mom_mexico", engine, if_exists = 'replace', index = True)

CPI_a12.to_sql("cpi_a12_mexico",engine, if_exists = 'replace', index = True)

CPI_acumulada_ano.to_sql("cpi_ytd_mexico",engine, if_exists = 'replace', index = True)

CPI_bi_weekly_indice.to_sql("cpi_biweekly_index_mexico",engine, if_exists = 'replace', index = True)

CPI_bi_weekly_mom.to_sql("cpi_biweekly_mom_mexico",engine, if_exists = 'replace', index = True)

CPI_indice.to_sql("cpi_index_mexico",engine, if_exists = 'replace', index = True)
        


#CPI_bi_weekly_mom_plot.total.unstack(level=-1).tail(8).plot(kind='bar')


# =============================================================================
# Gráficos para apresentação
# =============================================================================


cpi_a12 = pd.read_sql_query('SELECT * from cpi_a12_mexico',engine)\
            .dropna(axis=0,how='any')\
            .rename(columns = {'nao_subjacente':'não subjacente',
                               'agropecuaria':'agropecuária',
                               'energeticos_e_tarifas':'energéticos e tarifas'})

#bandas e meta

metas = pd.DataFrame([[2,3,4] for x in range(0,len(meta))]).rename(columns = {0:'banda inferior',
                                                                        1:'meta',
                                                                        2:'banda superior'})\
                .set_index(meta.index)
                
meta = pd.concat([meta,metas],axis=1)


# Metas e inflação
ax = meta[['banda inferior','banda superior']].plot(color='dimgrey',linestyle = '--')
plt.fill_between(meta.index,meta['banda inferior'],meta['banda superior'], color = 'lightgrey')
ax2 = meta.meta.plot(ax=ax, color = 'black', linestyle = '-.')
ax3=meta[['total','subjacente','não subjacente']].plot(ax=ax2)
ax3.legend(loc = 'upper left', fancybox = True, edgecolor = 'black',facecolor = 'white')

# Inflação por grupos, 2019

cpi_mom = pd.read_sql_query('SELECT * from cpi_mom_mexico',engine)\
            .set_index('dates',drop=True)\
            .dropna(how='any',axis=0)

cpi_mom.index = cpi_mom.index.strftime('%b/%Y')

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2,sharex=True,figsize=(15,9))

#Total

cpi_mom.tail(13).mercadorias.plot(ax=ax1,kind='bar',
            title = 'Mercadorias',colormap=cores)
labeling_bars(ax1,
              orientation = 'y',
          ratio = 1.05,
          offset_x = -0.4,
          fontsize = 10,
          fformat = '{:}')
ax1.get_yaxis().set_ticklabels([])

# Administrados
cpi_mom.tail(13).serviços.plot(ax=ax2,kind='bar',
            title='Serviços',colormap=cores)
labeling_bars(ax2,
              orientation = 'y',
          ratio = 1.05,
          offset_x = -0.4,
          fontsize = 10,
          fformat = '{:}')
ax2.get_yaxis().set_ticklabels([])


# Core
cpi_mom.tail(13).agropecuaria.plot(ax=ax3,kind='bar',title = 'Agropecuária',
            colormap=cores)
labeling_bars(ax3,
              orientation = 'y',
          ratio = 1.05,
          offset_x = -0.4,
          fontsize = 10,
          fformat = '{:}')
ax3.get_yaxis().set_ticklabels([])


# 
cpi_mom.tail(13).energeticos_e_tarifas.plot(ax=ax4,kind='bar',
            title = 'Energéticos e Tarifas',colormap=cores)
labeling_bars(ax4,
              orientation = 'y',
          ratio = 1.05,
          offset_x = -0.4,
          fontsize = 10,
          fformat = '{:}')
ax4.get_yaxis().set_ticklabels([])

fig.suptitle('CPI MoM por grupos')
plt.tight_layout()
fig.subplots_adjust(top=0.88)

# =============================================================================
# Heatmap
# =============================================================================

##### Importind data and deseasonalising #####

from statsmodels.tsa.x13 import x13_arima_analysis

cpi_index = pd.read_sql_query('SELECT * from cpi_index_mexico',engine)\
            .dropna(how='any',axis=0)\
            .set_index('dates',drop=True)

### Dessaz ###
x13_path = 'M:\\PUBLIC\\x13arima\\x13as.exe'

dessaz = pd.DataFrame(cpi_index.index).set_index('dates')

for column in cpi_index.columns:
    print(column)
    ts = cpi_index[column].dropna(axis=0)
    results = x13_arima_analysis(endog = ts,
                                log=None,
                                x12path = x13_path)
    seas = results.seasadj
    dessaz = pd.concat([dessaz,seas],axis=1)\
            .rename(columns = {'seasadj':column})
            
##### Heatmap #####
            
mapa = (dessaz.pct_change(1)*100).rolling(3).mean().tail(13)\
            .apply(lambda x: round(x,2))\
            .rename(columns = {'total':'Total',
                               'subjacente':'Core',
                               'mercadorias':'Bens',
                               'serviços':'Serviços',
                               'nao_subjacente':'Non-core',
                               'agropecuaria':'Alimentos',
                               'energeticos_e_tarifas':'Administrados'})

mapa.index = mapa.index.strftime('%b/%Y')

mapa = mapa.T

sns.set()

f, ax = plt.subplots(figsize = (15,9))
sns.heatmap(mapa,annot=True,linewidths=.5,ax=ax,cmap = plt.get_cmap('RdBu'),center=0)
ax.xaxis.set_ticks_position('top')
plt.yticks(rotation=0)




# =============================================================================
# Projeções 
# =============================================================================

tabela = pd.read_sql_query('SELECT * from bbm_eco',engine)\
            .dropna()\
            .drop('field',axis=1)

filtro = ['EHPIMXY Index',
'ECPIMX 19 Index',
'ECPIMX 19 Index',
'ECPIMX 20 Index',
'ECPIMX 21 Index',
'ECPIMX 19 SRV Index',
'ECPIMX 20 SRV Index',
'ECPIMX 21 SRV Index',
'ECPIMX 19 SRV Index',
'ECPIMX 20 SRV Index',
'ECPIMX 21 SRV Index',
'ECPIMX 19 NS Index',
'ECPIMX 20 NS Index',
'ECPIMX 21 NS Index',
'ECPIMX 19 BAR Index',
'ECPIMX 20 BAR Index',
'ECPIMX 21 BAR Index',
'ECPIMX 19 BOA Index',
'ECPIMX 20 BOA Index',
'ECPIMX 21 BOA Index',
'ECPIMX 19 CAG Index',
'ECPIMX 20 CAG Index',
'ECPIMX 21 CAG Index',
'ECPIMX 19 CSU Index',
'ECPIMX 20 CSU Index',
'ECPIMX 21 CSU Index',
'ECPIMX 19 FTC Index',
'ECPIMX 20 FTC Index',
'ECPIMX 21 FTC Index',
'ECPIMX 19 UBS Index',
'ECPIMX 20 UBS Index',
'ECPIMX 21 UBS Index',
'ECPIMX 19 DEK Index',
'ECPIMX 20 DEK Index',
'ECPIMX 21 DEK Index',
'ECPIMX 19 SCB Index',
'ECPIMX 20 SCB Index',
'ECPIMX 21 SCB Index',
'ECPIMX 19 CIT Index',
'ECPIMX 20 CIT Index',
'ECPIMX 21 CIT Index',
'ECPIMX 19 WF Index',
'ECPIMX 20 WF Index',
'ECPIMX 21 WF Index',
'ECPIMX 19 VPO Index',
'ECPIMX 20 VPO Index',
'ECPIMX 21 VPO Index',
'ECPIMX 19 SCI Index',
'ECPIMX 20 SCI Index',
'ECPIMX 21 SCI Index',
'ECPIMX 19 ABN Index',
'ECPIMX 20 ABN Index',
'ECPIMX 21 ABN Index',
'ECPIMX 19 JBC Index',
'ECPIMX 20 JBC Index',
'ECPIMX 21 JBC Index',
'ECPIMX 19 COM Index',
'ECPIMX 20 COM Index',
'ECPIMX 21 COM Index',
'ECPIMX 19 IG Index',
'ECPIMX 20 IG Index',
'ECPIMX 21 IG Index',
'ECPIMX 19 BXO Index',
'ECPIMX 20 BXO Index',
'ECPIMX 21 BXO Index',
'ECPIMX 19 BVA Index',
'ECPIMX 20 BVA Index',
'ECPIMX 21 BVA Index',
'ECPIMX 19 CE Index',
'ECPIMX 20 CE Index',
'ECPIMX 21 CE Index',
'ECPIMX 19 PMA Index',
'ECPIMX 20 PMA Index',
'ECPIMX 21 PMA Index',
'ECPIMX 19 HSB Index',
'ECPIMX 20 HSB Index',
'ECPIMX 21 HSB Index']

cpi = tabela[tabela.ticker.isin(filtro)].dropna()

cpi['ano_proj'] = cpi.ticker.str[7:9]

cpi['casa'] = cpi.ticker.str[10:13]

# escolher quais casas



