login = "dtshopenjoythemoment"
password = "oliveira09"

import json
import os
import time
from playwright.sync_api import sync_playwright

class BotElo7:
    url ='https://www.instagram.com/'
    login = "devmyprocess"
    password = "oliveira09"
    check_interval = 5

    def __init__(self, login, password, url, tag=None, text="", numb_of_comments=100, interval=10, send_message=False, number_of_users=0, use_backup=True) -> None:
        self.login = login
        self.senha = password
        self.url = url
        self.tag = tag
        self.text = text
        self.numb_of_comments = numb_of_comments
        self.interval = interval
        self.send_message = send_message
        self.number_of_users = number_of_users
        self.use_backup = use_backup


    def bot(self, playwright):

        chromium = playwright.chromium # or "firefox" or "webkit".
        browser = chromium.launch(headless = False)
        browser = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            viewport={ 'width': 640, 'height': 640 },
            locale='en'
        )
        page = browser.new_page()
        cookies = open('./cookies.json', 'r')
        cookies = cookies.read()

        page.context.add_cookies(eval(cookies))
        page.goto(self.url)
        
        page.wait_for_selector('body')
        is_logged = True if page.query_selector('input[name="username"]') is None else False
        if not is_logged:
            page.locator('input[name="username"]').type(self.login)
            page.locator('input[name="password"]').type(self.senha)
            page.locator('button[type="submit"]').click()
            page.wait_for_selector('svg[aria-label="Home"]')
                
            with open('./cookies.json','w') as file:
                file.write(str(page.context.cookies()))

        if self.tag is not None:
            page.goto(f'https://www.instagram.com/explore/tags/{self.tag}/')
            page.wait_for_selector('a > div > div > img[crossorigin="anonymous"]', timeout = 300000).click()
            if not self.send_message:
                number_of_likes_and_comments = 0
                while self.numb_of_comments > 0:
                    page.wait_for_selector('svg[aria-label="Like"]')
                    try:
                        like_selector = 'svg[aria-label="Like"]'
                        page.locator(like_selector).first.click() if page.query_selector(like_selector) is not None else ""
                        time.sleep(1)
                    except:
                        print('Is liked')

                    page.locator('svg[aria-label="Comment"]').first.click()
                    time.sleep(2)
                    page.fill('textarea[aria-label="Add a comment…"]', self.text)
                    time.sleep(1.5)
                    page.locator('form[method="POST"] textarea+div').click()
                    time.sleep(self.interval)
                    page.locator('svg[aria-label="Next"]').click()

                    number_of_likes_and_comments+=1
                    self.numb_of_comments -= 1
                    if number_of_likes_and_comments > 5:
                        time.sleep(60)
                        number_of_likes_and_comments = 0
                    else:
                        time.sleep(5)
            
            if self.send_message:
                if self.use_backup:
                    with open('./users.json', 'r') as file:
                        links = eval(file.read())
                else:
                    """
                    Remover duplicidade de usuarios
                    Ajustar o armazenamento de usuarios ja contactados
                    Rota para enviar mensagens para pessoas que curtiram posts referente a tag
                    """
                    page.locator('header span > div>  div > a[role="link"]').first.click()
                    page.wait_for_selector('section button div[dir="auto"]')
                    perfil = page.url.split('www.instagram.com/')[-1].replace('/','').strip()
                    followers_selector = f'a[href="/{perfil}/followers/"]'
                    page.locator(followers_selector).click()
                    before_number_of_links = 0
                    
                    while True:
                        page.wait_for_selector('._aano')
                        page.evaluate("document.querySelector('._aano').scroll({top: 100000, left: 0, behavior: 'smooth' })")
                        page.wait_for_selector('div[class=\"_aano\"] a[role=\"link\"]')
                        links = page.evaluate("Array.from(document.querySelectorAll('div[class=\"_aano\"] a[role=\"link\"]')).map(node => node.href)")
                        
                        if len(links)* 1.5 >= self.number_of_users :break
                        elif before_number_of_links == len(links) and links != []:break
                        else:before_number_of_links = len(links)
                    
                    links_copy = links.copy()
                    for i, link in enumerate(links_copy):
                        if i != 0 and i < len(links_copy)-1 and link == links[i-1]:
                            links.remove(link)
                        elif i > len(links_copy )-1:
                            break
                    with open('./users.json', 'w') as file:
                        file.write(str(links))

                number_of_users_sended_messages = 0
                db_of_users = links.copy()
                for link in links:
                    page.goto(link)
                    is_private_account = True if "private" in page.wait_for_selector('body').text_content().lower() else False
                    if is_private_account:
                        with open('./users.json', 'w') as file:
                            file.truncate(0)
                            db_of_users.remove(link)
                            file.write(str(db_of_users))
                        continue

                    send_message_selector_button = page.query_selector('section div:nth-child(3) div div:nth-child(2) > div[role="button"]')
                    if send_message_selector_button is None or send_message_selector_button.inner_text() == "":
                        page.locator('section button div[dir="auto"]').click()
                        page.reload()
                    
                    send_message_selector_button = page.wait_for_selector('section div:nth-child(3) div div:nth-child(2) > div[role="button"]')
                    send_message_selector_button.click()
                    page.wait_for_selector('div[role="textbox"]')
                    time.sleep(1)
                    dialog_button = 'button[tabindex="0"]:nth-child(2)'
                    page.click(dialog_button) if page.query_selector(dialog_button) is not None else ""
                    
                    array_of_text = self.text.split(" ")
                    each_of_text = " ".join(array_of_text[0:3]).strip()
                    text_in_chat = page.locator('div[data-pagelet="IGDOpenMessageList"]').text_content()
                    message_is_sended = each_of_text in text_in_chat
                    
                    if not message_is_sended:
                        try:
                            #send message in chat
                            page.fill('div[role="textbox"]', self.text)
                            page.click('div.xjyslct')
                        except:pass
                    else:
                        with open('./users.json', 'w') as file:
                            file.truncate(0)
                            db_of_users.remove(link)
                            file.write(str(db_of_users))
                        continue

                    time.sleep(5)
                    number_of_users_sended_messages +=1
                    if number_of_users_sended_messages >= 10:
                        time.sleep(120)
                        number_of_users_sended_messages = 0
                    else:
                        time.sleep(5)
                    
                    db_of_users.remove(link) if link in links else ""
                    with open('./users.json', 'w') as file:
                        file.truncate(0)
                        file.write(str(db_of_users))


            time.sleep(2)
            # page.click("textarea + div div[role='button']")
            print("The process is finalized or backup is empty")


    def sync_browser_instance(self):
        with sync_playwright() as playwright:
            try:return self.bot(playwright)
            except:os.system("taskkill /IM \"python.exe\" /F")
                
url ='https://www.instagram.com/'
login = "dtshopenjoythemoment"
password = "oliveira09"
text = """
Você já se perguntou como é viver em um ambiente perfeitamente equilibrado, onde o ar é fresco, a pele permanece hidratada e a saúde prospera? Pare de se perguntar e comece a experimentar a diferença com o nosso incrível Umidificador!

Benefícios para a Saúde:

    Respiração Mais Fácil

    Prevenção de Doenças

    Hidratação Interna

    Redução de Ronco

    Bem-estar Geral

Benefícios Principais:

    Ar Mais Puro e Fresco
    
    Pele Radiante

    Noites de Sono Repousantes

    Mente Mais Clara

    Design Elegante e Moderno

Transforme sua casa em um refúgio de bem-estar com o nosso Umidificador Portátil e Difusor de Aroma USB. Não deixe essa oportunidade passar. Compre agora e experimente a diferença que a hidratação pode fazer! Seu conforto e saúde merecem o melhor.
Garanta já o seu e aproveite a promoção por tempo ilimitado +30% OFF !

LINK: https://dtshopbr.lojavirtualnuvem.com.br/produtos/umidificador-portatil-difusor-de-aroma-usb/
PERFIL OFICIAL: @dtshop_enjoythemoment
"""
BotElo7(url=url, login = login, password=password, tag="umidificador", text=text, numb_of_comments=100, interval=10, send_message = False, number_of_users= 600, use_backup=False).sync_browser_instance()