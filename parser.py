import requests
from bs4 import BeautifulSoup


def img_parser(url):
    response = []
    while response == []:
        try:
            response = requests.get(url, allow_redirects=True, timeout=5)
        except:
            print('TimeOut Error')
            continue
    soup = BeautifulSoup(response.text, features="html.parser")

    #print(soup)

    res = soup.findAll(class_="autocover image__img image__landscape")
    res += soup.findAll(class_="autocover image__img image__portrait")
    images=[]
    print(len(res))

    for i in range(len(res)):
        #print(str(res[i]))
        index = str(res[i]).find("data-origin-src=")
        #print(index)
        #input()
        index += 17
        image = "https:"
        string = str(res[i])
        #print(string)
        #input()
        while string[index] != "\"":
            image += string[index]
            index += 1
        images.append(image)

    return images


'''
    for img in soup.findAll('div', img_class="autocover image__img image__portrait" ):
        
        if "products" in img.get('src'):
            if "http" in img.get('src'):
                if "74x74" in img.get('src'):
                    if (img in images):
                        continue
                        
        res = img.get('src')#.replace("74x74", "600x750")
        print(res)
        input()
                    # print(res)
                    '''

#print(img_parser("https://paypalshop.x.yupoo.com/albums/113597737?uid=1&tab=max"))
'''
u = input()
while u != 0:
    img_parser(u)
    u = input()
'''