import re
import json

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    entries = []
    current_entry = None
    
    current_pinyin = ''
    current_pos = ''
    current_meaning = None
    
    roman_numerals = ['ⅰ', 'ⅱ', 'ⅲ', 'ⅳ', 'ⅴ', 'ⅵ', 'ⅶ', 'ⅷ', 'ⅸ', 'ⅹ']
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 1. Check for top-level entry
        # e.g., "12、长cháng" or "1、爱"
        m_top = re.match(r'^(\d+)、\s*([\u4e00-\u9fa5]+)([a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]*)$', line)
        if m_top:
            current_entry = {
                'num': m_top.group(1),
                'char': m_top.group(2),
                'items': []
            }
            entries.append(current_entry)
            current_pinyin = m_top.group(3).strip()
            current_pos = ''
            current_meaning = None
            continue
            
        if not current_entry:
            continue
            
        # 2. Check for isolated pinyin
        if re.match(r'^[a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+$', line):
            current_pinyin = line.lower()
            current_pos = ''
            current_meaning = None
            continue
            
        # 3. Check for POS with or without meaning
        # e.g., "（1）名词。恩惠。（古之遗爱也《左传》）"
        m_pos = re.match(r'^（\d+）\s*(名词|动词|形容词|代词|副词|连词|介词|量词|数词|疑问代词|疑问副词|叹词|语气词|复合词|区别词)[。，：]*(.*)$', line)
        if m_pos:
            current_pos = m_pos.group(1)
            rest = m_pos.group(2).strip()
            if rest:
                current_meaning = {'pinyin': current_pinyin, 'pos': current_pos, 'meaning': rest, 'examples': []}
                current_entry['items'].append(current_meaning)
            else:
                current_meaning = None
            continue
            
        # 4. Check for meaning starters
        # ①加惠于人
        # 1、短，与“长”相对。
        # ⅰ、自称的谦词。
        # （1）如果不带POS的纯含义？（有些地方可能是 （3）表示被动）
        m_meaning = re.match(r'^([①-⑳]|\d+、|[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ]+、|（\d+）)(.*)$', line)
        if m_meaning:
            # wait, if it's "1、" but the line is exactly "1、长处", it matches.
            # but wait, is it possible to conflict with top-level?
            # Top-level is caught by m_top first! (because m_top strictly requires only Chinese chars after '、')
            rest = m_meaning.group(2).strip()
            if rest:
                current_meaning = {'pinyin': current_pinyin, 'pos': current_pos, 'meaning': rest, 'examples': []}
                current_entry['items'].append(current_meaning)
            continue
            
        # 5. It must be an example or a continuation
        if current_meaning is not None:
            current_meaning['examples'].append(line)
        else:
            # If we don't have a current meaning, maybe this line itself is a meaning item?
            # Like entry 45:
            # 区别：恨，憾，怨。“恨”和“憾”都表示遗憾。“怨”表示仇视、怀恨
            current_meaning = {'pinyin': current_pinyin, 'pos': current_pos, 'meaning': line, 'examples': []}
            current_entry['items'].append(current_meaning)
            
    # Post-process items to extract inline examples
    for entry in entries:
        for item in entry['items']:
            meaning = item['meaning']
            
            # Check for inline pinyin: "duó ,计算。" or "duó, 计算"
            m_inline_py = re.match(r'^([a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)\s*[,，]\s*(.*)$', meaning)
            if m_inline_py:
                item['pinyin'] = m_inline_py.group(1).lower()
                meaning = m_inline_py.group(2).strip()
            
            # Check for inline example: "加惠于人。（吴广素爱人。《陈涉世家》）"
            # It usually ends with "）"
            m_inline_ex = re.search(r'^(.*?)（([^）]+)）$', meaning)
            if m_inline_ex:
                clean_meaning = m_inline_ex.group(1).strip()
                example = m_inline_ex.group(2).strip()
                item['meaning'] = clean_meaning
                # we don't want to lose the parenthesis in the example for display?
                # Actually, the user's example in 국.csv had no parenthesis around the example text, 
                # but if the original txt has it, we can keep or strip. Let's keep it clean without outer parenthesis.
                item['examples'].insert(0, example)
            else:
                item['meaning'] = meaning

    with open('debug_parse.json', 'w', encoding='utf-8') as f:
        json.dump(entries[:5], f, ensure_ascii=False, indent=2)
        
if __name__ == '__main__':
    parse_file(r'd:\Github\single\anki-ewords\文言\150个文言文实词大全.txt')
