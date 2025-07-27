import os
import pandas as pd
import json


def add_table(table_url):
    print("Enter xlsx")
    # table_url = input()
    filename = 'table.json'
    with open(filename, 'w') as f_obj:
        json.dump(table_url, f_obj)
    print("F ok")


def load_table(table_url):
    filename = 'table.json'
    with open(filename) as f_obj:
        res = json.load(f_obj)
    if table_url == "":
        #print('ret', res)
        return res
    else:
        if res != table_url:
            print('Update xlsx')
            add_table(table_url)
    return table_url


def add_img(mas, table_url):
    #print('Zashlo', table_url)
    if not (os.path.exists('table.json')):
        add_table(table_url)
    #print("&&&")
    table_url = load_table(table_url)
    df = pd.read_excel(table_url)
    # print(df)
    new_id = df['ID'].max() + 1
    # print("o")

    mas[0] = new_id
    print(mas)

    if mas[13] in df["Ссылка"].unique():
        ind = df[df["Ссылка"] == mas[13]].index.values.astype(int)
        mas[0] = df.iloc[ind]["ID"]
        df.loc[ind] = [mas[0],
                       mas[1],
                       mas[2],
                       mas[3],
                       mas[4],
                       mas[5],
                       mas[6],
                       mas[7],
                       mas[8],
                       mas[9],
                       mas[10],
                       mas[11],
                       mas[12],
                       mas[13]
                       ]
        print(df.iloc[ind])
    else:
        df.loc[len(df)] = [mas[0],
                           mas[1],
                           mas[2],
                           mas[3],
                           mas[4],
                           mas[5],
                           mas[6],
                           mas[7],
                           mas[8],
                           mas[9],
                           mas[10],
                           mas[11],
                           mas[12],
                           mas[13]
                           ]

        print(df.iloc[len(df) - 1])
    # input("stop")
    df.to_excel(table_url, index=False)



