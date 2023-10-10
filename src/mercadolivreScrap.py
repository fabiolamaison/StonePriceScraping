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
    item_data = {'Names':[],'Prices':[],'Discounts':{'Amount':[],'Percentage':[]},'Review': {'Value': [],'Amount':[]},'Links':[], 'Popped':[]}

    # iteração para retirar os nomes de cada item, e descartar/limpar os que não contenham a palavra chave desejada (analisar caso a caso)
    for result in search_results:
        name = result.find('h2',{'class':'ui-search-item__title'}).text
        if name.lower().__contains__('pedra') or name.lower().__contains__('agata'):
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
        price = result.find('span',{'class':'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'}).find('span',{'class':'andes-visually-hidden'}).text    

        # capta, se existente, o valor original, que será utilizado para calcular o desconto ofertado
        try:
            original_val = result.find('s',{'class':'andes-money-amount ui-search-price__part ui-search-price__part--small ui-search-price__original-value andes-money-amount--previous andes-money-amount--cents-superscript andes-money-amount--compact'}).find('span',{'class':'andes-visually-hidden'}).text
        except:
            original_val = 'NaN'

        # as condicionais a seguir limpam o valor referente ao preço do produto
        if original_val.lower().__contains__('antes:'):

            original_val = original_val[(original_val.find(':')+2):]

        if price.lower().__contains__('centavos'):
            price = price[0:(price.find('reais')-1)] + '.' + price[(price.find('com')+4):(price.find('centavos')-1)]
        else:
            price = price[0:(price.find('reais')-1)] + '.00'

        # já essas condicionais limpam e calculam o valor referente ao disconto
        if original_val != 'NaN':
            if original_val.lower().__contains__('centavos'):
                original_val = original_val[0:(original_val.find('reais')-1)] + '.' + original_val[(original_val.find('com')+4):(original_val.find('centavos')-1)]
            else:
                original_val = original_val[0:(original_val.find('reais')-1)] + '.00'
            
            discount_val = float(original_val) - float(price)
            discount_pct = float(discount_val)/float(original_val)*100
            
        # guarda valores referente ao preço e descontos, caso existentes, do produto ofertado, nas respectivas chaves
        item_data['Prices'].append("{:.2f}".format(float(price)))
        item_data['Discounts']['Amount'].append("{:.2f}".format(float(discount_val)))
        item_data['Discounts']['Percentage'].append("{:.2f}".format(float(discount_pct)))
        
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

    print(item_data['Discounts'])
    print(item_data['Prices'])



getData(Links[0])