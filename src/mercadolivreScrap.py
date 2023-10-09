from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import csv
import os
import time
import pandas as pd

## Link de onde serão retirados os dados
Links = ['https://lista.mercadolivre.com.br/agata-azul-1kg#D[A:agata%20azul%201kg]']

## função para retirar os dados de cada item ofertado na página
def getData(link):

    source_html = requests.get(link)
    page_parser = bs(source_html.text,'html.parser')

    # variável que guarda todos os dados html dos itens ofertados, serve para toda página resultado de pesquisa do mercado livre
    search_results = page_parser.find('ol',{'class':'ui-search-layout ui-search-layout--stack'}).find_all('li',{'class':'ui-search-layout__item'})
    # variável criada para facilitar a limpeza dos dados durante iteração posterior.
    cleaned_results = search_results

    # dicionário que guardará os valores pertinentes dos itens desejados, contendo uma lista com o nome dos itens descartados para posterior analise
    item_data = {'Names':[],'Prices':[],'Review': {'Value': [],'Amount':[]},'Links':[], 'Popped':[]}

    # iteração para retirar os nomes de cada item, e descartar/limpar os que não contenham a palavra chave desejada (analisar caso a caso)
    for result in search_results:
        name = result.find('h2',{'class':'ui-search-item__title'}).text
        if name.lower().__contains__('pedra') == True:
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
        price = result.find('span',{'class':'andes-visually-hidden'}).text    

        # as condicionais a seguir limpam o valor referente ao preço do produto
        if price.lower().__contains__('antes:'):

            price = price[(price.find(':')+1):]

        if price.lower().__contains__('centavos'):
            price = price[0:(price.find('reais')-1)] + '.' + price[(price.find('com')+4):(price.find('centavos')-1)]
        else:
            price = price[0:(price.find('reais')-1)] + '.00'

        # guarda o valor do produto na chave 'prices' 
        item_data['Prices'].append(price)
        
        # capta o valor médio da review
        review_value = result.find('span',{'class':'ui-search-reviews__rating-number'})

        # tenta retirar o valor médio da review do html, caso ele não exista o define como 'NaN'
        try:
            review_value = review_value.text
        except:
            review_value = 'NaN'
        print(review_value)

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



getData(Links[0])