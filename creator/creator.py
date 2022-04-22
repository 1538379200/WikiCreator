import requests
import psycopg2
from functools import reduce


intab = '/'
outtab = '\\'
table_value = str.maketrans(intab, outtab)

wiki_header = {"Authorization":"Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjUwMDEzNzc0LCJleHAiOjE3NDQ2ODY1NzQsImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.UfJh_FMoZZyctce7Jy_pEL71ZWnFwvDdMwmPD6burlUg178kHLwjPWIfSNnKGrbWTHIlAJ7xK4taNLLZNYDf-l2UuaMiC06EfUjd6cDmi2yJcCTHxsK1eYjDtgcpZoNzVChHnSwsZk4EPekHxQK9-yRuo-26qyE_wBpok1D3oIna-qQN3FNs_Lhnviq2ReYnJaRKs6Urpwnch1GE24lY1Jaleqoj5hcIxqloa6ZSQg5tN2_w9yU6Rz2Hl3dcT8uj53xA0K6SPNFvH24O_5rA9_fQRYZtIugeUovgraCy_LOrVJFg8EkfHKkgRVa-FpNDxjFE6niJnzGbsSXxQDCEdg"}

def create_markdown(content, desc, path, tags, title):
    file_data = {"query": 'mutation{pages{create(content: """%s""",description: "%s",editor: "markdown",isPublished: true,isPrivate: false,locale: "zh",path: "%s",publishEndDate: "",publishStartDate: "",scriptCss: "",scriptJs: "",tags: "%s",title: "%s",){responseResult{succeeded errorCode slug message}}}}'%(content, desc, path, tags, title)}
    res = requests.post(url='http://39.98.138.157:8989/graphql', json=file_data, headers=wiki_header)
    return res

def upload_pic(file):
    url = 'http://39.98.138.157:8989/u'
    data = {'mediaUpload': '{"folderId":1}'}
    if '\\' in file:
        split_txt = '\\'
    else:
        split_txt = '/'
    file_name = file.split(split_txt)[-1]
    # print(file_name)
    pic = {
        'mediaUpload': (file_name, open(file, 'rb'), 'image/png')
    }
    res = requests.post(url=url, headers=wiki_header, data=data, files=pic)
    return res.text

def get_path():
    need_path = []
    all_path = []
    wiki_db = psycopg2.connect(database='wiki', user='wikijs', password='wikijsrocks', host='39.98.138.157', port='5432')
    cur = wiki_db.cursor()
    cur.execute('select p."path" from pages p;')
    rows = cur.fetchall()
    wiki_db.commit()
    cur.execute('select p.title  from pages p;')
    exist_file = cur.fetchall()
    wiki_db.commit()
    cur.close()
    wiki_db.close()
    path_list = [x[0] for x in rows]
    # print(path_list)
    for path_ in path_list:
        path_ = path_.split('/')[:-1]
        if path_:
            path_data = reduce(lambda x, y: x + '/' + y, path_)
            need_path.append(path_data)
    need_path = set(need_path)
    return need_path, path_list, exist_file


def read_md(file):
    content = ''
    img_path_list = []
    with open(file, 'r+', encoding='utf8') as f:
        file_data = f.readlines()
        for line in file_data:
            line = line.replace('\n', '').strip()
            if ('![' or '![[') in line:
                print('是图片', line)
                if ('http' or 'wiki-static') in line:
                    content = content + line + '\n'
                else:
                    if ')' in line:
                        imgname = line.split('[')[1].split(']')[0]
                        imgpath = line.split('(')[1].split(')')[0]
                        if imgname == '':
                            imgpath_copy = imgpath.translate(table_value)
                            imgname = imgpath_copy.split('\\')[-1].split('.')[0]
                    elif ']]' in line:
                        imgname = line.split('[[')[1].split(']]')[0].split('.')[0]
                        imgpath = ''
                    img_path_list.append(imgpath)
                    imgname = imgname.replace(' ', '_').replace('%20', '_')
                    imgname = imgname.lower()
                    print('图片名称', imgname)
                    line = f'![{imgname}](/wiki-static/{imgname}.png)'
                    content = content + line + '\n'
            else:
                content = content + line + '\n'
    return content, img_path_list
