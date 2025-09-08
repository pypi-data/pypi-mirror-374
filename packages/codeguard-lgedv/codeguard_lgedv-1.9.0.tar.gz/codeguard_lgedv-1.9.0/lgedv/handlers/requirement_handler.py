import os
import json
import re

def extract_requirements_from_md(md_path):
    """
    UNIVERSAL requirement extractor - tự động nhận diện patterns
    Hoạt động với mọi loại specification document
    """
    import re
    
    requirements = []
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Làm sạch content trước khi xử lý
    content = clean_content(content)
    
    # STRATEGY 1: Pattern-based extraction (universal)
    requirements.extend(extract_by_keywords(content))
    requirements.extend(extract_by_tables(content))
    requirements.extend(extract_by_numbering(content))
    requirements.extend(extract_by_sections(content))
    
    # STRATEGY 2: Keep existing usecase table logic
    requirements.extend(extract_usecase_table_original(content))
    
    # Remove duplicates
    requirements = deduplicate_requirements(requirements)
    
    return requirements

def clean_content(content):
    """Làm sạch content từ mọi loại markdown/HTML artifacts"""
    import re
    
    # Remove images
    content = re.sub(r'!\[.*?\]\([^)]*\)', '', content)
    
    # Remove HTML-like data URIs
    content = re.sub(r'data:image/[^)]*\)', '', content)
    
    # Remove excessive pipes and table artifacts
    content = re.sub(r'\|\s*\|\s*\|', '|', content)
    
    # Remove slide markers
    content = re.sub(r'<!-- Slide number: \d+ -->', '', content)
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    
    return content

def extract_by_keywords(content):
    """Extract bất kỳ text nào chứa requirement keywords"""
    import re
    
    requirements = []
    keywords = ['shall', 'must', 'should', 'required', 'mandatory', 'need to', 'have to']
    
    # Split thành các đoạn có nghĩa
    chunks = re.split(r'\n\s*\n|\. |\? |\! |。', content)
    
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if len(chunk) < 15:  # Skip quá ngắn
            continue
            
        # Check có keyword không
        if any(keyword in chunk.lower() for keyword in keywords):
            # Làm sạch thêm
            cleaned = re.sub(r'\|+', ' ', chunk)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if len(cleaned) > 20:
                requirements.append({
                    'id': f'KW-{i+1:04d}',
                    'description': cleaned,
                    'type': 'keyword_based',
                    'keywords_found': [kw for kw in keywords if kw in chunk.lower()]
                })
    
    return requirements

def extract_by_tables(content):
    """Extract từ bất kỳ table structure nào"""
    import re
    
    requirements = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Detect table row (có ít nhất 2 dấu |)
        if line.count('|') >= 2:
            # Skip table headers/separators
            if re.match(r'^\s*\|[\s\-\|]*\|\s*$', line):
                continue
                
            cells = [cell.strip() for cell in line.split('|')]
            cells = [cell for cell in cells if cell]  # Remove empty
            
            for j, cell in enumerate(cells):
                # Check cell có requirement không
                if any(keyword in cell.lower() for keyword in ['shall', 'must', 'should', 'required']):
                    if len(cell) > 20:
                        requirements.append({
                            'id': f'TBL-{i+1:04d}-{j+1:02d}',
                            'description': cell,
                            'type': 'table_based',
                            'line_number': i+1,
                            'column': j+1
                        })
    
    return requirements

def extract_by_numbering(content):
    """Extract từ bất kỳ numbered/lettered items"""
    import re
    
    requirements = []
    
    # Universal numbering patterns
    patterns = [
        r'^\s*(\d+(?:\.\d+)*)\s+(.+)',      # 1, 1.1, 1.2.3
        r'^\s*([a-z]\))\s+(.+)',            # a), b), c)
        r'^\s*([A-Z]\))\s+(.+)',            # A), B), C)
        r'^\s*(\d+\))\s+(.+)',              # 1), 2), 3)
        r'^\s*([IVX]+\))\s+(.+)',           # I), II), III)
        r'^\s*(\[\d+\])\s+(.+)',            # [1], [2], [3]
        r'^\s*([-*•])\s+(.+)',              # -, *, •
    ]
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                marker = match.group(1)
                text = match.group(2)
                
                # Check có requirement keywords không
                if any(keyword in text.lower() for keyword in ['shall', 'must', 'should', 'required']):
                    # Get context from surrounding lines
                    context = get_surrounding_context(lines, i)
                    
                    requirements.append({
                        'id': f'NUM-{marker}-{i+1:04d}',
                        'marker': marker,
                        'description': context or text,
                        'type': 'numbered',
                        'line_number': i+1
                    })
                break
    
    return requirements

def extract_by_sections(content):
    """Extract requirements organized by any section structure"""
    import re
    
    requirements = []
    
    # Find section boundaries (flexible patterns)
    section_patterns = [
        r'^(\d+(?:\.\d+)*)\s+([A-Z][^|]*)',      # 1 Title, 1.1 Title
        r'^([A-Z][A-Z\s]+)$',                     # ALL CAPS TITLES
        r'^(#{1,6})\s+(.+)',                      # Markdown headers
        r'^\s*([A-Z]\.|[IVX]+\.)\s+(.+)',        # A. Title, I. Title
    ]
    
    lines = content.split('\n')
    current_section = "Unknown"
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check if this is a section header
        is_section = False
        for pattern in section_patterns:
            match = re.match(pattern, line_stripped)
            if match:
                if len(match.groups()) >= 2:
                    current_section = f"{match.group(1)} {match.group(2)}"
                else:
                    current_section = match.group(1)
                is_section = True
                break
        
        # If not section header, check for requirements
        if not is_section and any(keyword in line_stripped.lower() for keyword in ['shall', 'must', 'should', 'required']):
            context = get_surrounding_context(lines, i)
            if context and len(context) > 25:
                requirements.append({
                    'id': f'SEC-{len(requirements)+1:04d}',
                    'section': current_section,
                    'description': context,
                    'type': 'section_based',
                    'line_number': i+1
                })
    
    return requirements

def get_surrounding_context(lines, center_idx, window=3):
    """Get context around a line"""
    import re
    
    start = max(0, center_idx - window)
    end = min(len(lines), center_idx + window + 1)
    
    context_lines = []
    for i in range(start, end):
        line = lines[i].strip()
        # Skip empty lines and artifacts
        if line and not re.match(r'^[\|\-\+\s\*#]*$', line):
            # Clean line
            cleaned = re.sub(r'\|+', ' ', line)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned and len(cleaned) > 3:
                context_lines.append(cleaned)
    
    return ' '.join(context_lines) if context_lines else None

def extract_usecase_table_original(content):
    """Keep original logic for backwards compatibility"""
    requirements = []
    lines = content.split('\n')
    in_table = False
    
    for line in lines:
        if '| TT | Tên Use-case' in line:
            in_table = True
            continue
        
        if in_table and line.strip() == '':
            break
            
        if in_table and line.startswith('|'):
            if '---' in line:
                continue
                
            parts = [part.strip() for part in line.split('|')[1:-1]]
            
            if len(parts) >= 8:
                tt = parts[0] if parts[0] != 'NaN' else ''
                usecase = parts[1] if parts[1] != 'NaN' else ''
                
                if usecase:
                    requirements.append({
                        'id': tt or f'UC-{len(requirements)+1:03d}',
                        'usecase': usecase,
                        'type': 'usecase_original'
                    })
    
    return requirements

def deduplicate_requirements(requirements):
    """Remove duplicates based on content similarity"""
    unique_reqs = []
    seen_content = set()
    
    for req in requirements:
        # Create a signature from description
        desc = req.get('description', '')
        if len(desc) > 50:
            signature = desc[:50].lower().strip()
        else:
            signature = desc.lower().strip()
        
        # Remove common words for better matching
        signature = re.sub(r'\b(the|and|or|of|in|to|for|with|by)\b', '', signature)
        signature = re.sub(r'\s+', ' ', signature).strip()
        
        if signature and signature not in seen_content:
            seen_content.add(signature)
            unique_reqs.append(req)
    
    return unique_reqs

def handle_requirement_analysis(dir_path: str):
    """Tool call: Phân tích requirement từ các file .md trong thư mục chỉ định."""
    try:
        if not os.path.exists(dir_path):
            return {"error": f"Thư mục không tồn tại: {dir_path}"}
        
        md_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
        
        if not md_files:
            return {"error": "Không tìm thấy file .md nào trong thư mục"}
        
        result = {}
        total_requirements = 0
        
        for md_file in md_files:
            file_path = os.path.join(dir_path, md_file)
            try:
                requirements = extract_requirements_from_md(file_path)
                result[md_file] = {
                    'total_requirements': len(requirements),
                    'requirements': requirements
                }
                total_requirements += len(requirements)
            except Exception as e:
                result[md_file] = {"error": str(e)}
        
        # Tạo summary
        summary = {
            'summary': {
                'total_files_analyzed': len(md_files),
                'total_requirements': total_requirements,
                'directory': dir_path
            },
            'files': result
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Lỗi khi phân tích requirement: {str(e)}"}