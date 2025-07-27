import requests

def f_prox():
    file = open("proxylist.txt", "r")
    res = []
    for line in file:
        line = line[:-1]
        new_line = "http://" + line
        res.append(new_line)
    file.close()
    return res


def choose_prox(n):
    print()


def to_normal_url(r):
    # Проверяем, что запрос успешен
    if r.status_code != 200:
        print(f"Ошибка API: {r.status_code} - {r.text}")
        return ""
    
    # Проверяем, что в ответе есть поле "link"
    if "\"link\":" not in r.text:
        print(f"Неожиданный ответ API: {r.text}")
        return ""
    
    index = r.text.find("\"link\":")
    index += 8
    answer = str(r.text)
    res_link = ""
    
    # Проверяем, что индекс не выходит за пределы строки
    if index >= len(answer):
        print("Ошибка парсинга: индекс выходит за пределы строки")
        return ""
    
    while index < len(answer) and answer[index] != "\"":
        if answer[index] == "\\":
            index += 1
            continue
        res_link += answer[index]
        index += 1
    
    # Проверяем, что получили валидный URL
    if not res_link.startswith("http"):
        print(f"Получен невалидный URL: {res_link}")
        return ""
    
    return res_link


def post_img_alternative(list_images):
    """Альтернативная функция - возвращает оригинальные URL без загрузки на Imgur"""
    print("Используем альтернативный режим - оригинальные URL")
    return list_images

def post_img(list_images, use_proxy=True):
    # Сначала пробуем Imgur API
    try:
        result = post_img_imgur(list_images, use_proxy)
        if any(url for url in result):  # Если хотя бы один URL получен
            return result
    except Exception as e:
        print(f"Ошибка Imgur API: {e}")
    
    # Если Imgur не работает, используем альтернативу
    print("Переключаемся на альтернативный режим")
    return post_img_alternative(list_images)

def post_img_imgur(list_images, use_proxy=True):
    res_links = []
    prox_list = f_prox() if use_proxy else []
    api = 'https://api.imgur.com/3/image'

    # Попробуем несколько client_id
    client_ids = [
        '546c25a59c58ad7',  # текущий
        '546c25a59c58ad8',  # альтернативный
        '546c25a59c58ad9'   # еще один
    ]
    
    current_client_id = 0

    j = 0  # Для прокси
    for i in range(len(list_images)):
        placeholder = str(list_images[i])
        
        # Пробуем разные client_id
        success = False
        for client_id_index in range(len(client_ids)):
            params = dict(
                client_id=client_ids[client_id_index]
            )
            
            files = dict(
                image=(None, placeholder),
                name=(None, ''),
                type=(None, 'URL'),
            )

            r = None  # Инициализируем переменную r
            
            # Сначала пробуем с прокси (если включены)
            if use_proxy and prox_list:
                while j < len(prox_list):
                    proxi = prox_list[j]
                    proxies = {
                        "https": str(proxi)
                    }
                    print(f"Прокси {prox_list[j]}: (client_id: {client_ids[client_id_index]})")

                    try:
                        r = requests.post(api, files=files, params=params, proxies=proxies)
                        print(r.text)
                        if r.text.find("over capacity") != -1:
                            print("Error: over capacity")
                            j += 1
                            continue
                        if r.text.find("You are uploading too fast") != -1:
                            print("Error: uploading too fast")
                            j += 1
                            continue
                        if r.status_code == 200:
                            success = True
                            break
                        else:
                            print(f"API Error: {r.status_code}")
                            j += 1
                            continue
                    except:
                        j += 1
                        print("Connection error")
                        continue

            # Если все прокси не работают или прокси отключены, пробуем без прокси
            if r is None or not success:
                print(f"Пробуем без прокси... (client_id: {client_ids[client_id_index]})")
                try:
                    r = requests.post(api, files=files, params=params)
                    print(r.text)
                    if r.text.find("over capacity") != -1:
                        print("Error: over capacity")
                        continue
                    if r.text.find("You are uploading too fast") != -1:
                        print("Error: uploading too fast")
                        continue
                    # Проверяем на ошибки API
                    if r.status_code == 200:
                        success = True
                        break
                    else:
                        print(f"API Error: {r.status_code}")
                        continue
                except Exception as e:
                    print(f"Ошибка при загрузке без прокси: {e}")
                    continue
            
            if success:
                break
        
        # Если ни один client_id не сработал, пропускаем изображение
        if not success:
            print(f"Не удалось загрузить изображение {i+1}: все client_id не работают")
            res_links.append("")
            continue

        # Проверяем, что r определена перед использованием
        if r is None:
            print(f"Не удалось загрузить изображение {i+1}: все методы не работают")
            res_links.append("")
            continue
            
        # Проверяем статус ответа
        if r.status_code != 200:
            print(f"Ошибка API для изображения {i+1}: {r.status_code}")
            res_links.append("")
            continue
            
        text = to_normal_url(r)
        print(text)
        res_links.append(text)
        
        # Добавляем задержку между запросами
        import time
        time.sleep(1)
        
    return res_links
