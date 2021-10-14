from datetime import date


def datecrypto():
    today = date.today()
    # dd/mm/YY
    d1 = today.strftime("%d/%m/%Y")
    data1 = d1.replace("/", "i")
    data2 = data1.replace("0", "j")
    data3 = data2.replace("1", "k")
    data4 = data3.replace("2", "l")
    data5 = data4.replace("3", "m")
    data6 = data5.replace("4", "n")
    data7 = data6.replace("5", "o")
    data8 = data7.replace("6", "p")
    data9 = data8.replace("7", "q")
    data10 = data9.replace("8", "r")
    data11 = data10.replace("9", "s")
    return data11
