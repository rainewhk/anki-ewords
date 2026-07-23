import re
import csv
import os

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    entries = []
    current_entry = None
    
    current_pinyin = ''
    current_pos = ''
    current_meaning = None
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        m_top = re.match(r'^(\d+)、\s*([\u4e00-\u9fa5]+)([a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]*)$', line)
        if m_top:
            current_entry = {
                'num': m_top.group(1),
                'char': m_top.group(2),
                'items': []
            }
            entries.append(current_entry)
            current_pinyin = m_top.group(3).strip().lower()
            current_pos = ''
            current_meaning = None
            continue
            
        if not current_entry:
            continue
            
        if re.match(r'^[a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+$', line):
            current_pinyin = line.lower()
            current_pos = ''
            current_meaning = None
            continue
            
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
            
        m_meaning = re.match(r'^([①-⑳]|\d+、|[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ]+、|（\d+）)(.*)$', line)
        if m_meaning:
            starter = m_meaning.group(1)
            rest = m_meaning.group(2).strip()
            
            if starter.startswith('（'):
                current_pos = ''
                
            if rest:
                current_meaning = {'pinyin': current_pinyin, 'pos': current_pos, 'meaning': rest, 'examples': []}
                current_entry['items'].append(current_meaning)
            continue
            
        if current_meaning is not None:
            current_meaning['examples'].append(line)
        else:
            current_meaning = {'pinyin': current_pinyin, 'pos': current_pos, 'meaning': line, 'examples': []}
            current_entry['items'].append(current_meaning)
            
    for entry in entries:
        for item in entry['items']:
            meaning = item['meaning']
            
            m_inline_py = re.match(r'^([a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)\s*[,，]\s*(.*)$', meaning)
            if m_inline_py:
                item['pinyin'] = m_inline_py.group(1).lower()
                meaning = m_inline_py.group(2).strip()
            
            # Match (example) at the end of the line
            m_inline_ex = re.search(r'^(.*?)（([^）]+)）$', meaning)
            if m_inline_ex:
                clean_meaning = m_inline_ex.group(1).strip()
                example = m_inline_ex.group(2).strip()
                item['meaning'] = clean_meaning
                item['examples'].insert(0, example)
            else:
                item['meaning'] = meaning

    return entries

def generate_csv(entries, output_path):
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for entry in entries:
            num = entry['num']
            char = entry['char']
            key = f"【实词{num}】{char}"
            
            html_rows = []
            for item in entry['items']:
                pinyin = item.get('pinyin', '')
                pos = item.get('pos', '')
                meaning = item.get('meaning', '')
                
                parts = []
                if pinyin:
                    parts.append(f"[{pinyin}]")
                if pos and not meaning.startswith(pos):
                    parts.append(f"【{pos}】")
                parts.append(meaning)
                
                anki_key = " ".join(parts).strip()
                
                clean_examples = []
                for ex in item.get('examples', []):
                    ex = ex.strip()
                    if ex.startswith('（') and ex.endswith('）'):
                        ex = ex[1:-1]
                    clean_examples.append(ex)
                
                anki_val = "<br>".join(clean_examples)
                
                if not anki_key and not anki_val:
                    continue
                    
                row_html = f'''    <tr>
      <td class="anki-key">{anki_key}</td>
      <td class="anki-val">{anki_val}</td>
    </tr>'''
                html_rows.append(row_html)
                
            if not html_rows:
                continue
                
            tbody_content = '\n'.join(html_rows)
            full_html = f'''<table class="anki-table">
  <tbody>
{tbody_content}
  </tbody>
</table>'''
            writer.writerow([key, full_html])

if __name__ == '__main__':
    base_dir = r"d:\Github\single\anki-ewords\文言"
    input_file = os.path.join(base_dir, "150个文言文实词大全.txt")
    output_file = os.path.join(base_dir, "150个文言文实词大全.csv")
    entries = parse_file(input_file)
    generate_csv(entries, output_file)
    print("Done generating 150个文言文实词大全 CSV.")
