from sympy.ntheory import totient
from tkinter import messagebox


# Функция проверки числа на простоту
def is_prime_number(number):
    k = 0
    for i in range(2, number // 2+1):
        if number % i == 0:
            k += 1
    if k <= 0:
        return True
    return False


# Функция генерации хэша
def hash_(text, p):
    h = [0]
    for char in text:
        h.append((h[-1]+int(char))**2 % p)
    return h[-1]


# Функция умножения точек
def doubling_P(P, a, p):
    lam = ['', '']
    lam[0] = (3 * P[0] ** 2 + a) % p
    lam[1] = 2 * P[1] % p
    if not (lam[0]/lam[1]).is_integer():
        lam[0] = lam[0] % p
        lam[1] = (lam[1] ** (totient(p) - 1)) % p
        lam = int(lam[0] * lam[1] % p)
    else:
        lam = int(lam[0]/lam[1])
    x = (lam ** 2 - 2 * P[0]) % p
    y = (lam * (P[0] - x) - P[1]) % p
    return x, y


# Функция сложения точек
def addition_P(P1, P2, p):
    lam = ['', '']
    lam[0] = (P2[1] - P1[1]) % p
    lam[1] = (P2[0] - P1[0]) % p
    if not (lam[0]/lam[1]).is_integer():
        lam[0] = lam[0] % p
        lam[1] = (lam[1] ** (totient(p) - 1)) % p
        lam = int(lam[0] * lam[1] % p)
    else:
        lam = int(lam[0]/lam[1])
    x = (lam ** 2 - P1[0] - P2[0]) % p
    y = (lam * (P1[0] - x) - P1[1]) % p
    return x, y


# Функция генерации ключа
def key_gen(P, k, a, p):
    k = bin(k)[3:]
    P_ = P
    for i in k:
        P_ = doubling_P(P_, a, p)
        if i == '1':
            P_ = addition_P(P, P_, p)
    return P_


# Функция преобразования сообщения в числовой формат (unicode)
def message_to_pos_unicode(message):
    new_message = []
    for i in message:
        new_message.append(('0' * (4 - len(str(ord(i)))) + str(ord(i))))
    return new_message


# Функция генерации подписи
def generation_signature(message, math_params):
    message_ = message_to_pos_unicode(message)
    hash = hash_(message_, math_params["p"])
    if hash == 0:
        hash = 1
    yu = key_gen(math_params["G"], math_params["xu"], math_params["a"], math_params["p"])
    P = key_gen(math_params["G"], math_params["p"], math_params["a"], math_params["p"])
    r = math_params["P"][0] % math_params["q"]
    s = (math_params["k"] * hash + r * math_params["xu"]) % math_params["q"]
    return message, r, s, yu


# Функция проверки подписи
def signature_verification(message, r, s, yu, p, a, G, q):
    message_ = message_to_pos_unicode(message)
    hash = hash_(message_, p)
    if hash == 0:
        hash = 1
    u1 = s * hash ** (totient(q) - 1) % q
    u2 = (-r * hash ** (totient(q) - 1)) % q
    P1 = key_gen(G, u1, a, p)
    P2 = key_gen(yu, u2, a, p)
    P = addition_P(P1, P2, p)
    if P[0] % q == r:
        messagebox.showinfo('info', f'x mod q ({P[0] % q}) = r({r}) => Подпись верна')
    else:
        messagebox.showerror('Error', f'Подпись не верна. x mod q = {P[0] % q}, а r = {r}')


# Функция генерации подписи
def encrypt(message, a, p, G, q, closed_key, random_k):
    # Проверки
    if not is_prime_number(p):
        messagebox.showerror('Error', 'p должно быть простым')
        return
    try:
        G = list(map(int, G.split()))
    except:
        messagebox.showerror('Error', 'G введено неверно')
        return

    if closed_key <= 0 or closed_key >= q:
        messagebox.showerror('Error', f'Xu должно быть в диапазоне (0; {q})')
    while random_k <= 0 or random_k >= q:
        messagebox.showerror('Error', f'k должно быть в диапазоне (0; {q})')
    xu = closed_key % q
    k = random_k % q
    math_params = {
        "xu": xu,
        "k": k,
        "p": p,
        "a": a,
        "G": G,
        "q": q
    }
    return generation_signature(message, math_params)


# Функция проверки подписи
def decrypt(message, signature_1, signature_2, p, a, G, q, open_key):
    try:
        G = list(map(int, G.split()))
    except:
        messagebox.showerror('Error', 'G введено неверно')
        return
    try:
        open_key = list(map(int, open_key.split()))
    except:
        messagebox.showerror('Error', 'Открытый ключ введено неверно')
        return
    return signature_verification(message, signature_1, signature_2, open_key, p, a, G, q)
