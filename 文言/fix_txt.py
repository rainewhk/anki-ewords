import io

def fix_file(filepath):
    with io.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply fixes
    content = content.replace('nè；名词', 'nèi；名词')
    content = content.replace('ná；<u>通“纳”', 'nà；<u>通“纳”')
    content = content.replace('zhi： <u>通“智”', 'zhì： <u>通“智”')
    content = content.replace('金 qiān：<u>皆', '佥 qiān：<u>皆')
    content = content.replace('jī：几次', 'jǐ：几次')
    content = content.replace('shui：劝说', 'shuì：劝说')
    content = content.replace('yòu：<u>计谋', 'yóu：<u>计谋')
    content = content.replace('篝阸的中心', '箭靶的中心')
    content = content.replace('254. 贵：zī', '254. 赀：zī')
    content = content.replace('<u>通“资”钱财</u>258. 雅', '<u>通“资”钱财</u>\n258. 雅')
    content = content.replace('谱 zèn 润', '谮 zèn 润')
    content = content.replace('左丘失明，有《国语》', '左丘失明，厥有《国语》')
    
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_file(r'd:\Github\single\anki-ewords\文言\国.txt')
    print("Fixed text file.")
