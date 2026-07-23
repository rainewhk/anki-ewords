import re
import csv
import os

def parse_pinyin_and_typos(details):
    # Replace colon after pinyin with semicolon
    details = re.sub(r'([a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)\s*[：:]', r'\1；', details)
    # Replace colon after parenthesis with semicolon
    details = re.sub(r'[）)]\s*[：:]', r'）；', details)
    return details

def split_details(details):
    segments = []
    current = []
    paren_depth = 0
    in_u_tag = False
    i = 0
    while i < len(details):
        if details[i:i+3] == '<u>':
            in_u_tag = True
            current.append('<u>')
            i += 3
            continue
        elif details[i:i+4] == '</u>':
            in_u_tag = False
            current.append('</u>')
            i += 4
            continue
        
        char = details[i]
        if char in '（(':
            paren_depth += 1
            current.append(char)
        elif char in '）)':
            paren_depth -= 1
            current.append(char)
        elif char in '；;' and paren_depth == 0 and not in_u_tag:
            segments.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
        i += 1
    if current:
        segments.append(''.join(current).strip())
    
    # Clean up trailing periods
    cleaned = []
    for s in segments:
        s = s.strip('。.')
        if s:
            cleaned.append(s)
    return cleaned

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all entries: <number>.<char>：<details>
    pattern = re.compile(r'(\d+)[.．]\s*([^：\n]+)：\s*(.*?)(?=(?:\n\s*\d+[.．])|(?:\d+[.．]\s*[^：\n]+：)|$)', re.DOTALL)
    
    entries = pattern.findall(content)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for num, char, details in entries:
            num = num.strip()
            char = char.strip()
            details = details.strip()
            
            key = f"【国{num}】{char}"
            
            details = parse_pinyin_and_typos(details)
            segments = split_details(details)
            
            html_rows = []
            current_pinyin = ""
            
            for seg in segments:
                match = re.search(r'^(.*?)[（(](.*?)[）)]$', seg)
                if match:
                    meaning = match.group(1).strip()
                    example = match.group(2).strip()
                else:
                    meaning = seg.strip()
                    example = ""
                
                # Check if this segment is purely pinyin
                # Pinyin might contain latin letters and tone marks
                if re.match(r'^[a-zA-Zǎáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+$', meaning):
                    current_pinyin = meaning
                    continue # Skip emitting a row for the pinyin itself
                
                # Prefix meaning with pinyin if we have one
                display_meaning = f"[{current_pinyin}] {meaning}" if current_pinyin else meaning
                
                # Format each row
                row_html = f'''    <tr>
      <td class="anki-key">{display_meaning}</td>
      <td class="anki-val">{example}</td>
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
    input_file = os.path.join(base_dir, "国.txt")
    output_file = os.path.join(base_dir, "国.csv")
    process_file(input_file, output_file)
    print("Done generating CSV.")
