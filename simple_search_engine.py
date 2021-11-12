import re
import xlrd


def read_data(d_id, c, u):
    location = ("IR_Spring2021_ph12_7k.xlsx")
    wb = xlrd.open_workbook(location, encoding_override="UTF-16")
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)

    for i in range(1, sheet.nrows):
        d_id.append(int(sheet.row_values(i)[0]))
        c.append(sheet.row_values(i)[1])
        u.append(sheet.row_values(i)[2])


def tokenizer(token_doc, c):
    for i in range(len(c)):
        # for remove email from doc
        c[i] = re.sub(r'[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,3}', '', c[i])
        # for remove url from doc
        c[i] = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
                      c[i])
        # for remove english words and [.?!-* and others] and digits
        c[i] = re.sub(r'[A-Za-z]+|[^A-Za-z\w\s-]+', '', c[i])
        c[i] = re.sub(r'[-]', ' ', c[i])
        c[i] = re.sub(r'\d', '', c[i])
        c[i] = re.sub(r'_', '', c[i])
        # for remove é
        c[i] = re.sub('é', '', c[i])

        c[i] = c[i].replace("می ", "می" + "\u200c")

        tokens = c[i].split()
        for t in tokens:
            token_doc.append([t, i + 1])


def remove_Suffix(t):
    if t.endswith("تر") and len(t) > 4:
        t = t[:-2]
    elif t.endswith("ترین"):
        t = t[:-4]
    elif t.endswith("های"):
        t = t[:-3]
    elif t.endswith("ها"):
        t = t[:-2]
    elif t.endswith("ات"):
        t = t[:-2]
    elif t.endswith("ان"):
        t = t[:-2]

    return t


def remove_prefix(t):
    if t.startswith("بر"):
        t = t[2:]
    elif t.startswith("در"):
        t = t[2:]

    return t


def normalization(t):
    t = t.replace("آ", "ا")
    t = t.replace("ّ", "")
    t = t.replace("ي", "ی")
    t = t.replace("ك", "ک")
    if t.endswith("ء"):
        t = t[:-1]

    return t


def verb_rooting(t):
    m_roots = ["گفت", "رفت", "دید", "شد", "زد", "داد", "کرد", "نوشت", "بود", "یافت", "خواست", "داشت"]
    mz_roots = ["کن", "بین", "گردان", "رس", "دار", "توان", "باش", "گیر"]

    suffix = ["م", "ی", "ید", "یم", "ند", "ه"]
    for r in m_roots:
        if t.__contains__(r):
            if t.__contains__("می‌" + r):
                return r
            for s in suffix:
                if t.__contains__(r + s):
                    return r

    suffix = ["م", "ی", "ید", "یم", "ند", "د"]
    for rz in mz_roots:
        if t.__contains__("می‌" + rz):
            return rz
        for s in suffix:
            if t.__contains__(rz + s):
                return rz
    return t


def stemming(token_doc, token_num):
    for t in token_doc:
        doc_id = t[1]
        word = t[0]
        word = remove_Suffix(word)
        word = remove_prefix(word)
        word = normalization(word)
        word = verb_rooting(word)
        t[0] = word

        try:
            token_num[t[0]] += 1
        except KeyError:
            token_num[t[0]] = 1


def stop_word(token_doc, stop_w, term_doc):
    for t in token_doc:
        if not stop_w.__contains__(t[0]):
            term_doc.append([t[0], t[1]])

            # try:
            #     term_fre[(t[0], t[1])] += 1
            # except KeyError:
            #     term_fre[(t[0], t[1])] = 1


def indexer(term_doc, inverted_index):
    term_doc.sort(key=lambda x: x[0])
    tmp = None
    count = 1
    postings_list = []

    for t in term_doc:
        if tmp == t[0] and t[1] not in postings_list:
            count += 1
            postings_list.append(t[1])

        elif tmp is None:
            tmp = t[0]
            postings_list.append(t[1])

        elif tmp != t[0]:
            inverted_index.append((tmp, count, postings_list))
            tmp = t[0]
            count = 1
            postings_list = [t[1]]


def test(data):
    while True:
        t = input("do you  do the test?[y-n]\n")
        if t == "y":
            word = input("please input your word: ")
            flag = False
            for d in data:
                if d[0] == word:
                    flag = True
                    print(d[2])
                    break
            if not flag:
                print("No Match found!\n")
        else:
            break


def answer_query(data, stop_word, u):
    while True:
        queries = input("query: ").split()
        tokens = []
        token_num = {}
        tokenizer(tokens, queries)
        stemming(tokens, token_num)
        q = []
        for k, v in token_num.items():
            if k and k != ' ' and not stop_word.__contains__(k):
                q.append(k)
        if len(q) == 0:
            print("No Match found!\n")
        elif len(q) == 1:
            flag = False
            for d in data:
                if d[0] == q[0]:
                    flag = True
                    print(d[2])
                    for indexi in d[2]:
                        print(url[indexi-1])
                    break
            if not flag:
                print("No Match found!\n")
        else:
            word_count = {}
            for w in q:
                for d in data:
                    if d[0] == w:
                        for c in d[2]:
                            try:
                                word_count[c] += 1
                            except KeyError:
                                word_count[c] = 1
                        break
            print("dict: ", word_count, "\n")
            word = sorted(word_count, key=word_count.get, reverse=True)
            print(word)
            for indexi in word:
                print(url[indexi - 1])


if __name__ == "__main__":
    document_id = []
    contents = []
    url = []
    read_data(document_id, contents, url)
    token_doc = []
    token_number = {}
    term_doc = []
    inverted_index = []

    tokenizer(token_doc, contents)
    stemming(token_doc, token_number)
    stop_words = sorted(token_number, key=token_number.get, reverse=True)[:20]
    stop_word(token_doc, stop_words, term_doc)

    indexer(term_doc, inverted_index)
    test(inverted_index)

    answer_query(inverted_index, stop_words, url)
