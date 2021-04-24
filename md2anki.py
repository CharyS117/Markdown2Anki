import os
import platform
import shutil
import pandas as pd


def JudgeMtime(filePath, outPath):
    if os.path.exists(outPath):
        if os.stat(outPath).st_mtime >= os.stat(filePath).st_mtime:
            return 0
    return 1


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


if __name__ == '__main__':
    separator = '\n\n%\n\n'
    fold = '/Users/chary/Dropbox/md2anki'  # working fold
    AnkiMediaFold = '/Users/chary/Library/Application Support/Anki2/chary/collection.media'
    mdfileFold = fold + '/mdfile'  # fold to store .md file to convert
    csvFold = fold + '/csv'  # output .csv fold
    picFold = fold + '/pic'  # fold to store pics to move to Anki media fold
    # pic import
    pics = os.listdir(picFold)
    for pic in pics:
        if pic[0] != '.' and pic[0:5] != 'IMPT_':  # mark transferred pics
            picPath = os.path.join(picFold, pic)
            shutil.copyfile(picPath, os.path.join(AnkiMediaFold, pic))
            os.rename(picPath, os.path.join(picFold, 'IMPT_' + pic))
    filenames = os.listdir(mdfileFold)
    # md2anki
    for filename in filenames:
        if filename[-3:] != '.md':
            continue
        tempPath = os.path.join(fold, filename)
        filePath = os.path.join(mdfileFold, filename)
        csvPath = os.path.join(csvFold, filename[:-3] + '.csv')
        if JudgeMtime(filePath, csvPath) == 0:
            continue
        # numberate mdfile
        with open(filePath, 'r') as og:
            ogdata = og.readlines()
            outdata = []
            isTitle = 2
            num = {}
            for line in ogdata:
                if line == '\n':
                    outdata.append(line)
                    continue
                if isTitle == 2:
                    isTitle = 0
                    dotIndex = line.find('. ')
                    if dotIndex == -1:
                        outdata.append(line)
                        continue
                    if line[0:dotIndex] not in num:
                        num[line[0:dotIndex]] = 1
                    outdata.append(line[:dotIndex] + '.' +
                                   str(num[line[0:dotIndex]]) +
                                   line[dotIndex:])
                    num[line[0:dotIndex]] = num[line[0:dotIndex]] + 1
                    continue
                if line == '%\n':
                    isTitle = isTitle + 1
                    outdata.append(line)
                    continue
                outdata.append(line)
            with open(tempPath, 'w') as out:
                for line in outdata:
                    out.write(line)
        # md2csv
        with open(tempPath, 'r') as og:
            og_data = og.read()
            og_list = og_data.split(separator)
            if len(og_list) % 2 == 1:
                og_list.append('')
            df = pd.DataFrame(og_list[1::2], index=og_list[::2])
            df.to_csv(csvPath, encoding='utf_8_sig', columns=None, header=None)
        with open(csvPath, 'r') as csv:
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
            with open(csvPath, 'w') as csv:
                for i in dl:
                    csv.write(i)
            # open in preview (only on macos)
            if platform.system() == 'Darwin':
                os.system('qlmanage -p \'' + csvPath + '\'')
        os.remove(tempPath)
