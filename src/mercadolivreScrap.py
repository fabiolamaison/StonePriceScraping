from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import csv
import os
import time
import pandas as pd
import copy

## Link de onde serão retirados os dados
Links = ['https://lista.mercadolivre.com.br/ametista-1kg_NoIndex_True']

def pages_link(link,pages):
    rg = list(range(51,((pages+1)*50+1),50))
    links = []
    for num in rg:
        new_link = link[0:link.find('NoIndex')] + 'Desde_' + str(num) + link[link.find('_NoIndex'):]
        links.append(new_link)
    return links

def contains_keywords(string, keys):
    for key in keys:
        if key in string:
            return True
    return False

## função para retirar os dados de cada item ofertado na página
def getData(link, key_words = ''):

    source_html = requests.get(link)
    page_parser = bs(source_html.text,'html.parser')

    # variável que guarda todos os dados html dos itens ofertados, serve para toda página resultado de pesquisa do mercado livre
    search_results = page_parser.find('ol',{'class':'ui-search-layout ui-search-layout--stack'}).find_all('li',{'class':'ui-search-layout__item'})

    buebue_results = page_parser.find('ol',{'class':'ui-search-layout ui-search-layout--stack'}).find_all('li',{'class':'ui-search-layout__item','style':'display: none !important;'})

    # variável criada para facilitar a limpeza dos dados durante iteração posterior.
    cleaned_results = copy.copy(search_results)

    # dicionário que guardará os valores pertinentes dos itens desejados, contendo uma lista com o nome dos itens descartados para posterior analise
    item_data = {'Names':[],'Prices':[],'Discounts':{'Amount':[],'Percentage':[]},'Review': {'Value': [],'Amount':[]},'Links':[], 'Popped':[]}

    # iteração para retirar os nomes de cada item, e descartar/limpar os que não contenham a palavra chave desejada (analisar caso a caso)
    for result in search_results:

        name = result.find('h2',{'class':'ui-search-item__title'}).text
        if contains_keywords(name, key_words) or key_words == '':
            item_data['Names'].append(name)
        else:
            item_data['Popped'].append(name)
            cleaned_results.pop(cleaned_results.index(result))
    
    # utilizando a lista já limpa de resultados, esta iteração retira o valor do produto, dados sobre as avaliações, e guarda seu respectivo link
    for result in cleaned_results:

        # capta os links
        link = result.find('a',{'class':'ui-search-item__group__element ui-search-link'})['href']
        # realiza append do link na lista de links
        item_data['Links'].append(link)

        # capta o preço
        price = float(result.find('span',{'class':'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'}).text[2:].replace(',','.'))

        # capta, se existente, o valor original, que será utilizado para calcular o desconto ofertado
        try:
            original_val = float(result.find('s',{'class':'andes-money-amount ui-search-price__part ui-search-price__part--small ui-search-price__original-value andes-money-amount--previous andes-money-amount--cents-superscript andes-money-amount--compact'}).text[2:].replace(',','.'))

        except:
            original_val = 0.0


        if original_val != 0.0:  
            discount_val = original_val - price
            discount_pct = discount_val/original_val*100
        else:
            discount_val = 0.0
            discount_pct = 0.0
        
        # guarda valores referente ao preço e descontos, caso existentes, do produto ofertado, nas respectivas chaves
        item_data['Prices'].append("{:.2f}".format(price))
        item_data['Discounts']['Amount'].append("{:.2f}".format(discount_val))
        item_data['Discounts']['Percentage'].append("{:.2f}".format(discount_pct))
        
        # capta o valor médio da review
        review_value = result.find('span',{'class':'ui-search-reviews__rating-number'})

        # tenta retirar o valor médio da review do html, caso ele não exista o define como 'NaN'
        try:
            review_value = review_value.text
        except:
            review_value = 'NaN'
        

        # realiza append da variável contendo a média de reviews à chave 'Value' dentro de 'Review'
        item_data['Review']['Value'].append(review_value)

        

        # capta o total de reviews
        review_value = result.find('span',{'class':'ui-search-reviews__amount'})

        # tenta retirar a quantidade de reviews do html, caso ele não exista o define como 'NaN'
        try:
            review_value = review_value.text[1:-1]
        except:
            review_value = 'NaN'

        # realiza append da variável contendo a quantidade de reviews à chave 'Amount' dentro de 'Review'
        item_data['Review']['Amount'].append(review_value)

    return item_data

# Função que por momento não está sendo utilizada, constrói com listas um header de dois leveis a partir de um dicionário aninhado
def get_header(dictionary, level1=None, level2=None, current_key=''):
    if level1 is None:
        level1 = []
    if level2 is None:
        level2 = []

    for key, value in dictionary.items():
        # Check if the value is a dictionary
        if isinstance(value, dict):
            level1.append(key)
            level1.extend(['']*(len(value)-1))
            for key in value:
                level2.append(key)
        else:
            # If the value is not a dictionary, add a blank space to level2
            level2.append(key)
            level1.append('')
    print(level1, level2)
    return level1, level2

# Planariza o dicionário, unindo chaves e 'sub-chaves'
def planarize_dictionary(input_dict, parent_key='', separator='_'):

    result = {}
    for key, value in input_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            result.update(planarize_dictionary(value, new_key, separator))
        else:
            result[new_key] = value
    return result

# item_data = getData(Links[0])

# item_data.pop('Popped')

# dct = planarize_dictionary(item_data)

# item_df = pd.DataFrame(dct)
# print(item_df)

def generateLink(pesquisa):
    link = 'https://lista.mercadolivre.com.br/' + str(pesquisa).replace(' ','-') + '_NoIndex_True'
    print(link)
    return link

pages_links = pages_link(generateLink('arroz branco'),10)
print(pages_links)

def join_dicts(dict1, dict2):
    joined_dict = {}
    if not dict1:
        return dict2
    else:
        for key in set(dict1) | set(dict2):
            joined_dict[key] = dict1.get(key, []) + dict2.get(key, [])
        return joined_dict

def multiScrap(links, key_words = ''):

    all_data = {}

    for link in links:
        try:
            data = getData(link, key_words)
            data.pop('Popped')
            plan_data = planarize_dictionary(data)
            key_val = list(plan_data.keys())[0]
            key_len = len(plan_data[key_val])
            print('Original dict len: ' + str(key_len))
            all_data = join_dicts(all_data, plan_data)
            key_val = list(all_data.keys())[0]
            key_len = len(all_data[key_val])
            print('Main dict len: ' + str(key_len))


        except:
            print('Foram processados ' + str(links.index(link)+1) + ' links')
            break

    main_df = pd.DataFrame(all_data)
    main_df.to_csv('G:/Workspace/WebScrap/backData/test.csv')
    print(main_df)


multiScrap(pages_links)