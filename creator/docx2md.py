import docx
import time
from functools import reduce
import re


class Docx2Md:
    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.doc = docx.Document(self.doc_path)

    def get_name(self):
        time_ = time.strftime("%Y%m%d%H%M%S")
        return time_

    def get_doc_img(self):
        pic_info_dict = {}
        all_rel = self.doc.part._rels   # 获取所有资源
        for rel in all_rel:     # 循环资源列表
            rel = all_rel[rel]      # 通过键值对，取出值
            # print(rel.target_ref)
            if 'image' in rel.target_ref:       # 如果这个包含'image'则进行下面操作
                imgname = rel.target_ref.split('/')[1].split('.')[0]        # 切分成image1的格式
                doc_path_split = self.doc_path.split('\\')      # 将传入的文件路径切分
                # print('传入doc', doc_path_split)
                filter_path = doc_path_split[:-1]
                # print(filter_path)
                root_path = reduce(lambda x, y: x + '\\' + y, filter_path)      # 取出文件拼凑成路径
                imgname = imgname + '-' + self.get_name()   # 拼接成新的图片名称
                pic_path = root_path + '\\' + imgname + '.png'      # 拼接新图片存放路径(包含文件名和扩展名)
                with open(pic_path, 'wb') as f:     # 保存图片文件
                    f.write(rel.target_part.blob)
                pic_info_dict[imgname] = pic_path
        return pic_info_dict

    def docx2md(self):
        md_content = ''
        pic_index = 0
        pic_dict = self.get_doc_img()
        keys_list = sorted(list(pic_dict.keys()), key=lambda x: int(re.findall('\d+', x)[0]))
        for line in self.doc.paragraphs:     # 遍历doc文本的所有段落（paragraph）
            if 'docPr' in line._element.xml:    # 如果这段的xml元素中包含“docPr”，就证明这里有图片
                img_num = line._element.xml.count("docPr")      # 获取此段落的图片总数
                for i in range(img_num):        # 循环此段落中所有的“docPr”，标记为图片+index
                    # print(f"图片{pic_index}")
                    pic_dict_key = keys_list[pic_index]
                    pic_text = f'![{pic_dict_key}](/wiki-static/{pic_dict_key}.png)'
                    # print(pic_text)
                    md_content = md_content + pic_text + '\n'
                    pic_index += 1
            else:                           # 如果段落中没有图片，进入下面的处理
                name = line.style.name      # style.name可以标记是normal还是heading标题，查询这段落的style.name
                if 'Heading 1' in name:     # 如果中间包含“Heading 1”说明是一级标题，给开头加上“#”
                    title_mark = '# '
                elif 'Heading 2' in name:   # 如果包含“Heading 2”说明为二级标题，给开头加“##”，只写到四级标题
                    title_mark = '## '
                elif "Heading 3" in name:
                    title_mark = "### "
                elif "Heading 4" in name:
                    title_mark = "#### "
                else:                       # 如果所有的都不满足，则认定为正文，直接输出
                    title_mark = ''
                line_text = title_mark + line.text
                md_content = md_content + line_text + '\n'
                # print(line_text)
        # print(md_content)
        return md_content, list(pic_dict.values())

# if __name__ == '__main__':
#     pic_info = Docx2Md(r'C:\Users\cema\Desktop\测试文档.docx').docx2md()



