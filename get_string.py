def to_string(mas, f_mas):
    res = ""
    if len(mas) == 0 or len(f_mas) == 0:
        return
    maxm = max(f_mas)
    while maxm != 0:
        minm = maxm
        for i in range(len(f_mas)):
            if f_mas[i] < minm and f_mas[i] != 0:
                minm = f_mas[i]
                #print (minm)
        ind = f_mas.index(minm)
        #print(ind)
        #print(mas[ind])
        res += mas[ind] + '\n'
        #print(res)
        f_mas[ind] = 0
        maxm = max(f_mas)
        #print(maxm, minm, ind, f_mas)
        #input()
    return res