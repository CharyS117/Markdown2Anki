import pandas as pd
import os

separator = '\n\n'
outPath = './'
filePath = './'

def JudgeMath(dl, i):
    if len(dl) > 1:
        if i != 0 and i != len(dl) - 1:
            if dl[i + 1] == '$':
                return 1
            if dl[i - 1] != '$':
                return 0
        if i == 0:
            if dl[i + 1] != '$':
                return 0
            else:
                return 1
        if i == len(dl):
            if dl[i - 1] != '$':
                return 0


def JudgeBold(dl, i):
    if len(dl) > 1:
        if i != 0 and i != len(dl) - 1:
            if dl[i + 1] == '*':
                return 1
            if dl[i - 1] != '*':
                return 0
        if i == 0:
            if dl[i + 1] != '*':
                return 0
            else:
                return 1
        if i == len(dl):
            if dl[i - 1] != '*':
                return 0

def JudgeMtime(filePath,outPath):
    if os.path.exists(outPath):
        if os.stat(outPath).st_mtime >= os.stat(filePath).st_mtime:
            return 0
    return 1

filenames = os.listdir(filePath)
outnames = []
i = 0
n = len(filenames)
while i < n:
    if '.md' in filenames[i]:
        outnames.append(os.path.join(outPath, filenames[i][:-3]+'.csv'))
        filenames[i] = os.path.join(filePath,filenames[i])
        i = i + 1
    else:
        filenames.pop(i)
        n = n - 1
for p in range(len(filenames)):
    if JudgeMtime(filenames[p],outnames[p]) == 0:
        continue
    with open(filenames[p], 'r') as og:
        og_data = og.read()
        og_list = og_data.split(separator)
        if len(og_list) % 2 == 1:
            og_list.append('')
        df = pd.DataFrame(og_list[1::2], index=og_list[::2])
        df.to_csv(outnames[p],
                  encoding='utf_8_sig',
                  columns=None,
                  header=None)
    with open(outnames[p], 'r') as csv:
        math_k = 0
        bold_k = 0
        quotes_k = 0
        data = csv.read()
        dl = list(data)
        for i in range(len(dl) - 1):
            if dl[i] == '$':
                math = JudgeMath(dl, i)
                if math == 0:
                    if math_k == 0:
                        dl[i] = '\\('
                        math_k = 1
                    else:
                        dl[i] = '\\)'
                        math_k = 0
                if math == 1:
                    if math_k == 0:
                        dl[i] = '\\['
                        dl[i + 1] = ''
                        math_k = 1
                    else:
                        dl[i] = '\\]'
                        dl[i + 1] = ''
                        math_k = 0
            if dl[i] == '*' and math_k == 0:
                bold = JudgeBold(dl, i)
                if bold == 0:
                    if bold_k == 0:
                        dl[i] = '<i>'
                        bold_k = 1
                    else:
                        dl[i] = '</i>'
                        bold_k = 0
                if bold == 1:
                    if bold_k == 0:
                        dl[i] = '<b>'
                        dl[i + 1] = ''
                        bold_k = 1
                    else:
                        dl[i] = '</b>'
                        dl[i + 1] = ''
                        bold_k = 0
            if dl[i] == '<' and math_k == 1:
                dl[i] = '&lt;'
            if dl[i] == '>' and math_k == 1:
                dl[i] = '&gt;'
            if dl[i] == '"':
                if quotes_k == 0:
                    quotes_k = 1
                else:
                    quotes_k = 0
            if quotes_k == 1 and dl[i] == '\n':
                dl[i] = '<br>'
        with open(outnames[p], 'w') as csv:
            for i in dl:
                csv.write(i)
