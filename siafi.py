# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:49:24 2020

@author: rafael.lincoln
"""

import requests
import pandas as pd
import re
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import getpass
import time
import os
import shutil
import numpy as np

wd = 'M:\\06_ECONOMIA\\Dados\\Brasil\\Fiscal\\SIAFI'
os.chdir(wd)

LS = os.listdir
DOWNLOAD_path = f"C:\\Users\\{getpass.getuser()}\\Downloads"


link = "http://www9.senado.leg.br/QvAJAXZfc/opendoc.htm?document=Senado%2FSigaBrasilPainelEspecialista.qvw&host=QVS%40www9&anonymous=true&select=LB137"


chrome_path = "M:\\PUBLIC\\Codes\\chromedriver_80.exe"



driver = webdriver.Chrome(chrome_path)

driver.get(link)
time.sleep(20)

fxpath = driver.find_element_by_xpath

# =============================================================================
# Despesas
# =============================================================================

# Fiscal / Seguridade >> Gráficos customizados
#fxpath(r'/html/body/div[5]/div/div[31]/div[2]/table/tbody/tr/td').click()

fxpath('/html/body/div[5]/div/div[73]/div[2]/table/tbody/tr/td').click()


dictio = {"Dimensão":{
        'Período':['Ano Execução','Mês Execução (Número)'],
        'Categoria Econômica':['Categoria Econômica (Desc)'],
        'Unidade Orçamentária':['UO (Cód)'],
        'GND':['GND (Desc)'],
        'Elemento Despesa':['Elemento Despesa (Desc)']},
        "Métrica":{
        'Despesa Executada':['Despesa Executada (R$)']}}


time.sleep(10)

# Selecionar opções

for metric in dictio:
    lista = dictio[metric]
    for element in lista:
        for item in lista[element]:
            search_word = metric + "|" + element + "|" + item
            # Clicar na search box
            time.sleep(1)
            fxpath('//*[@id="127"]/div[1]/div[1]/div').click()
            # Pesquisar e clicar
            time.sleep(1)
            fxpath('/html/body/div[2]/input').send_keys(search_word)
            time.sleep(1)
            fxpath(f"//*[@title='{search_word}']").click()
            time.sleep(3)


# Baixar o CSV

fxpath('//*[@id="130"]/div[1]/div[1]/div[2]').click()
#element = WebDriverWait(driver, 5).until(
#        EC.presence_of_element_located((By.XPATH, "\\*[text='O conteúdo solicitado foi aberto em outra janela.']"))
#    )
time.sleep(60)
filename = max([os.path.join(DOWNLOAD_path,f) for f in LS(DOWNLOAD_path) ],key=os.path.getctime)
shutil.move(filename, os.path.join(os.getcwd(),'SIAFI_Despesas.csv'))

#### Filtrando os dados ####

# Pegar planilha
despesas = pd.read_csv(os.path.join(os.getcwd(),'SIAFI_Despesas.csv'), header = 0).dropna()\
                .rename(columns = {'Despesa Executada (R$)':'Despesa'})

# preparar filtro
despesas = despesas[despesas['Mês (Número) DES'] != 0]

## Fazer a mudança nos números para transformá-los em int

# despesas

despesas['Despesa'] = [x.replace('- ','-') for x in [x.replace(',','.') for x in [x.replace('.','') for x in despesas['Despesa']]]]

# Transformar em numérico

cols = ['Mês (Número) DES',
        'Ano',
        'Despesa',
        'UO (Cod) DESP']



despesas[cols] = despesas[cols].apply(pd.to_numeric, errors = 'coerce').dropna(axis = 0)

despesas = despesas.dropna(0).rename(columns = {'UO (Cod) DESP':'uo',
                                                'Mês (Número) DES':'mes',
                                                'Ano':'ano'})

despesas = despesas[despesas.Despesa != 0]
    
    
# arrumar datas

despesas['data'] = (despesas.ano.apply(round).apply(str) + '-' + despesas.mes.apply(round).apply(str) + '-01').apply(pd.to_datetime)

despesas = despesas.drop(columns = ['ano','mes'])

## Catalogação das despesas
#
#rgps = {'RGPS':25917}
#
#pessoal = { }





# =============================================================================
# Receitas
# =============================================================================

# Receita >> Gráficos Customizados (caso dê problema, ir na página do SIAFI e inspecionar elemento,
#procurando o full xpath do botão de receita e tentando novamente)

fxpath(r'/html/body/div[5]/div/div[28]/div[2]/table/tbody/tr/td').click()



time.sleep(3)


fxpath(r'/html/body/div[5]/div/div[58]/div[2]/table/tbody/tr/td').click()


# retirar o filtro dos anos

time.sleep(3)

fxpath('/html/body/div[6]/div/div[112]/div[2]/div[2]/img').click()
fxpath('//*[@id="225"]/div[2]/table/tbody/tr/td').click()
fxpath('/html/body/div[5]/div/div[64]/div[2]/div/div[1]/div[16]/div[1]').click()


dictio = {"Dimensão":{
        'Período da Execução':['Ano','Mês (Número)'],
        'Fonte':['Fonte (Cód)'],
        'Natureza da Receita':['Natureza da Receita (Desc)','Natureza da Receita (Cód)'],
        'Grupo Classificação Receita':['Grupo Classificação Receita (Desc)'],
        'Classificação Receita':['Classificação Receita (Desc)']},
        "Metrica":{
        'Previsão Atualizada':['Previsão Atualizada (R$)'],
        'Arrecadação':['Arrecadação (R$)']}}
    
time.sleep(5)

# Selecionar opções

for metric in dictio:
    lista = dictio[metric]
    for element in lista:
        for item in lista[element]:
            search_word = metric + ">" + element + ">" + item
            # Clicar na search box
            time.sleep(1)
            fxpath('/html/body/div[5]/div/div[76]/div[1]/div[1]/div').click()
            # Pesquisar e clicar
            time.sleep(1)
            fxpath('/html/body/div[2]/input').send_keys(search_word)
            time.sleep(1)
            fxpath(f"//*[@title='{search_word}']").click()
            time.sleep(3)


fxpath('//*[@id="206"]/div[1]/div[1]/div[2]').click()
time.sleep(60)
filename = max([os.path.join(DOWNLOAD_path,f) for f in LS(DOWNLOAD_path) ],key=os.path.getctime)
shutil.move(filename, os.path.join(os.getcwd(),'SIAFI_Receitas.csv'))

#### Receitas ####

## Pegar planilha
receitas = pd.read_csv(os.path.join(os.getcwd(),'SIAFI_Receitas.csv'),
                       header = 0).dropna()

# receitas = pd.read_excel('SIAFI_receitas.xlsx',
#                          header=0).dropna()

## Fazer a mudança nos números para transformá-los em int

# arrecadação

receitas['Arrecadação'] = [x.replace('- ','-') for x in [x.replace(',','.') for x in [x.replace('.','') for x in receitas['Arrecadação']]]]


# Previsão

receitas['Previsão Atualizada'] = [x.replace('- ','-') for x in [x.replace(',','.') for x in [x.replace('.','') for x in receitas['Previsão Atualizada']]]]


cols = ['Natureza Receita (Cod) Rec','Fonte (Cod) Rec','Arrecadação','Previsão Atualizada','Ano Receita','Mês (Número) Rec']

receitas[cols] = receitas[cols].apply(pd.to_numeric, errors = 'coerce').dropna(axis = 0)

receitas = receitas.dropna(0)

## Datas

receitas = receitas[receitas['Mês (Número) Rec'] != 0]

receitas.drop('Grupo Classificação Receita Rec',axis=1,inplace=True)
# consertar datas

receitas.columns = ['nome','codigo','fonte','classificacao','ano','mes','arrecadacao','previsto']


receitas['data'] = (receitas.ano.apply(round).apply(str) + '-' + receitas.mes.apply(round).apply(str) + '-01').apply(pd.to_datetime)

receitas = receitas.drop(columns = ['ano','mes'])

##################### Catalogação das receitas por código #####################

# Receita Total

serie_receita_total = receitas.groupby('data').sum().arrecadacao



IPI = {11140131:'IPI - Automóveis',
        11140121:'IPI - Bebidas',
        11140111:'IPI - Fumo',
        11140158:'IPI - Outros',
        11140157:'IPI - Outros',
        11140152:'IPI - Outros',
        11140151:'IPI - Outros',
        11140141:'IPI - Vinculado a Importação'}

IR = {11130112:'IR - PF',
        11130113:'IR - PF',
        11130321:'IR - Rendimentos do Capital',
        11130341:'IR - Outros Rendimentos',
        11130331:'IR - Remessa ao Exterior',
        11130311:'IR - Rendimentos do Trabalho',
        11130118:'IR - PF',
        11130117:'IR - PF',
        11130111:'IR - PF',
        11130213:'IR - PJ',
        11130218:'IR - PJ',
        11130217:'IR - PJ',
        11130212:'IR - PJ',
        11130211:'IR - PJ'}

COFINS = {12114918:'COFINS',
            12114917:'COFINS',
            12110116:'COFINS',
            12110118:'COFINS',
            12110115:'COFINS',
            12110117:'COFINS',
            12114916:'COFINS',
            12114915:'COFINS',
            12110216:'COFINS',
            12110215:'COFINS',
            12114913:'COFINS',
            12114911:'COFINS',
            12110211:'COFINS',
            12110113:'COFINS',
            12110111:'COFINS',
            12100113:'COFINS',
            12100118:'COFINS',
            12100117:'COFINS',
            12100112:'COFINS',
            12100111:'COFINS'}

PIS = {72120112:'PIS/PASEP',
        72120111:'PIS/PASEP',
        12124913:'PIS/PASEP',
        12124912:'PIS/PASEP',
        12124914:'PIS/PASEP',
        12124911:'PIS/PASEP',
        12120113:'PIS/PASEP',
        12120112:'PIS/PASEP',
        12120114:'PIS/PASEP',
        12120111:'PIS/PASEP',
        12120212:'PIS/PASEP',
        12120211:'PIS/PASEP',
        72120115:'PIS/PASEP',
        12120118:'PIS/PASEP',
        12120117:'PIS/PASEP',
        12120128:'PIS/PASEP',
        12120127:'PIS/PASEP',
        12124918:'PIS/PASEP',
        12124917:'PIS/PASEP',
        12120116:'PIS/PASEP',
        12120115:'PIS/PASEP',
        12120123:'PIS/PASEP',
        12120126:'PIS/PASEP',
        12120125:'PIS/PASEP',
        12120121:'PIS/PASEP',
        12124916:'PIS/PASEP',
        12124915:'PIS/PASEP'}

CSLL = {12134913:'CSLL',
            12134911:'CSLL',
            12130113:'CSLL',
            12130111:'CSLL',
            12130118:'CSLL',
            12130117:'CSLL',
            12130116:'CSLL',
            12130115:'CSLL',
            12130128:'CSLL',
            12130127:'CSLL',
            12130123:'CSLL',
            12130126:'CSLL',
            12130125:'CSLL',
            12130121:'CSLL',
            12134918:'CSLL',
            12134917:'CSLL',
            12134916:'CSLL',
            12134915:'CSLL',
            12100213:'CSLL',
            12100218:'CSLL',
            12100217:'CSLL',
            12100212:'CSLL',
            12100211:'CSLL'}

CIDE = {12200828:'CIDE',
      12200827:'CIDE',
      12200823:'CIDE',
      12200824:'CIDE',
      12200822:'CIDE',
      12200821:'CIDE',
      12200813:'CIDE',
      12200812:'CIDE',
      12200811:'CIDE'}

RGPS = {12190911:'RGPS',
        19900312:'RGPS',
        19900311:'RGPS',
        12140124:'RGPS',
        12140123:'RGPS',
        12140122:'RGPS',
        12140121:'RGPS',
        12140113:'RGPS',
        12140114:'RGPS',
        12140112:'RGPS',
        12140111:'RGPS',
        12140213:'RGPS',
        12140212:'RGPS',
        12140214:'RGPS',
        12140211:'RGPS',
        12100313:'RGPS',
        12100314:'RGPS',
        12100312:'RGPS',
        12144913:'RGPS',
        12144914:'RGPS',
        12144912:'RGPS',
        12144911:'RGPS',
        12100311:'RGPS',
        12140001:'RGPS',
        19101112:'RGPS',
        19101111:'RGPS',
        19100914:'RGPS',
        19100912:'RGPS',
        19100913:'RGPS',
        19100911:'RGPS',
        19100414:'RGPS',
        19100413:'RGPS',
        19100313:'RGPS',
        19100312:'RGPS',
        19101213:'RGPS',
        19100113:'RGPS',
        19100114:'RGPS',
        19100112:'RGPS',
        19100111:'RGPS',
        79100111:'RGPS',
        19100513:'RGPS',
        19100512:'RGPS',
        19100511:'RGPS',
        19100311:'RGPS',
        19100412:'RGPS',
        19100411:'RGPS',
        19101013:'RGPS',
        19101014:'RGPS',
        19101011:'RGPS',
        19100211:'RGPS',
        19230412:'RGPS',
        19230411:'RGPS',
        19221311:'RGPS',
        19220312:'RGPS',
        19220311:'RGPS'}

exploracao_rec_natural = {13440213:'Exploração de Recursos Naturais',
                            13440211:'Exploração de Recursos Naturais',
                            13440113:'Exploração de Recursos Naturais',
                            13440111:'Exploração de Recursos Naturais',
                            13450112:'Exploração de Recursos Naturais',
                            13450111:'Exploração de Recursos Naturais',
                            13410121:'Exploração de Recursos Naturais',
                            13410421:'Exploração de Recursos Naturais',
                            13410431:'Exploração de Recursos Naturais',
                            13410441:'Exploração de Recursos Naturais',
                            13410341:'Exploração de Recursos Naturais',
                            13410321:'Exploração de Recursos Naturais',
                            13410331:'Exploração de Recursos Naturais',
                            13410311:'Exploração de Recursos Naturais',
                            13410241:'Exploração de Recursos Naturais',
                            13410221:'Exploração de Recursos Naturais',
                            13410231:'Exploração de Recursos Naturais',
                            13410211:'Exploração de Recursos Naturais',
                            13430241:'Exploração de Recursos Naturais',
                            13450323:'Exploração de Recursos Naturais',
                            13450321:'Exploração de Recursos Naturais',
                            13450311:'Exploração de Recursos Naturais'}

concessoes = {16400211:'Concessões e Permissões',
                13460122:'Concessões e Permissões',
                13460121:'Concessões e Permissões',
                13460111:'Concessões e Permissões',
                13100212:'Concessões e Permissões',
                13100211:'Concessões e Permissões',
                73100211:'Concessões e Permissões',
                13330031:'Concessões e Permissões',
                13330011:'Concessões e Permissões',
                13310211:'Concessões e Permissões',
                13310111:'Concessões e Permissões',
                13320411:'Concessões e Permissões',
                13320311:'Concessões e Permissões',
                13320121:'Concessões e Permissões'}

sal_educ = {12190411:'Contribuição do salário educação'}

IOF = {11150123:'IOF',
        11150128:'IOF',
        11150127:'IOF',
        11150122:'IOF',
        11150121:'IOF',
        11150112:'IOF',
        11150111:'IOF'}

importacao = {11110113:'Imposto sobre Importação',
                11110118:'Imposto sobre Importação',
                11110117:'Imposto sobre Importação',
                11110112:'Imposto sobre Importação',
                11110111:'Imposto sobre Importação'}

tipos = [IPI,IR,COFINS,CSLL,PIS,CIDE,RGPS,exploracao_rec_natural,concessoes,sal_educ,IOF,importacao]



idx = pd.IndexSlice


correspondencia = pd.concat([pd.DataFrame([item]).T for item in tipos]).rename(columns = {0:'grupos'})




receitas = pd.merge(receitas,correspondencia.reset_index(), left_on='codigo', right_on ='index').rename(columns = {0:'grupos'})

receitas = receitas[receitas['data'] > '2016-01-01']

receitas_final = receitas.groupby(['data','grupos']).sum().arrecadacao

# =============================================================================
# Manipulações das receitas
# =============================================================================

# YoY

lista = list(set([x for x in receitas_final.index.get_level_values(1)]))


yoy = pd.DataFrame()
for element in lista:
    yoy[element] = receitas_final.loc[idx[:,element,:]].pct_change(12)*100    

yoy.reset_index(level = 0, inplace=True)

excel_mom = pd.melt(yoy, id_vars = ['data'],value_vars=yoy.columns[2:len(yoy.columns)], var_name='grupos',value_name='mom')


# MoM


mom = pd.DataFrame()
for element in lista:
    mom[element] = receitas_final.loc[idx[:,element,:]].pct_change(1)*100

mom.reset_index(level = 0, inplace=True)

excel_yoy = pd.melt(mom, id_vars = ['data'],value_vars=mom.columns[2:len(mom.columns)], var_name='grupos',value_name='yoy')


# Tabela para Excel/SQL

excel = pd.concat([receitas_final,excel_yoy.set_index(['data','grupos']),excel_mom.set_index(['data','grupos'])],axis=1).reset_index()

from sqlalchemy import create_engine

engine = create_engine('mysql://economistas:Mudar2019@@10.100.1.8/economia')

excel.to_sql("siafi_receita", engine, if_exists = 'replace', index = False)



