import re
from typing import Dict, List, Tuple
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


def analyze_cognitive_complexity(c_code: str) -> Tuple[int, List[Dict]]:
    lines = c_code.strip().split('\n')
    total_score = 0
    line_analysis = []
    nesting_level = 0
    logical_operator_sequences = set()

    # Очистка кода от комментариев
    cleaned_lines = []
    in_block_comment = False

    for line in lines:
        clean_line = line.strip()

        # Обработка многострочных комментариев
        if '/*' in clean_line and '*/' in clean_line:
            clean_line = re.sub(r'/\*.*?\*/', '', clean_line)
        elif '/*' in clean_line:
            in_block_comment = True
            clean_line = clean_line.split('/*')[0]
        elif '*/' in clean_line:
            in_block_comment = False
            clean_line = clean_line.split('*/')[1] if '*/' in clean_line else ''
        elif in_block_comment:
            clean_line = ''

        # Удаляем однострочные комментарии
        if '//' in clean_line:
            clean_line = clean_line.split('//')[0]

        if clean_line.strip():
            cleaned_lines.append(clean_line.strip())

    # Основной анализ когнитивной сложности
    for line_num, line in enumerate(cleaned_lines, 1):
        line_score = 0
        details = []
        current_nesting = nesting_level

        # Определяем структуры, увеличивающие сложность
        structures = {
            'if': r'if\s*\(',
            'else if': r'else\s+if\s*\(',
            'else': r'else\s*[^{]',
            'for': r'for\s*\(',
            'while': r'while\s*\(',
            'do': r'do\s*[^{]',
            'switch': r'switch\s*\(',
            'case': r'case\s+',
            'default': r'default\s*:',
            'try': r'try\s*[^{]',
            'catch': r'catch\s*\(',
            'finally': r'finally\s*[^{]',
            'goto': r'goto\s+\w+',
            'break': r'break\s*;',
            'continue': r'continue\s*;',
            'return': r'return\s*[^;]',
            '&&': r'&&',
            '\|\|': r'\|\|',
            'ternary': r'\?.*:',
            'nested': r'\{',
            'end_block': r'\}',
            'function': r'(\w+)\s+(\w+)\s*\(',
            'recursion': r'(\w+)\s*\(.*\1\s*\('
        }

        # Проверяем каждую структуру
        for struct, pattern in structures.items():
            matches = re.findall(pattern, line)
            if matches:
                if struct in ['if', 'else if', 'for', 'while', 'switch', 'catch']:
                    # Базовое увеличение за прерывание потока
                    line_score += 1
                    details.append(f"{struct}: +1 (прерывание потока)")

                    # Учет вложенности
                    if current_nesting > 0:
                        line_score += current_nesting
                        details.append(f"{struct}: +{current_nesting} (вложенность)")

                elif struct == 'else':
                    line_score += 1
                    details.append(f"else: +1 (альтернативный путь)")

                elif struct in ['case', 'default']:
                    line_score += 1
                    details.append(f"{struct}: +1 (ветвление)")

                elif struct in ['&&', '||']:
                    # Учет последовательностей логических операторов
                    if struct not in logical_operator_sequences:
                        logical_operator_sequences.add(struct)
                        line_score += 1
                        details.append(f"логический оператор {struct}: +1 (последовательность)")

                elif struct == 'ternary':
                    line_score += 1
                    details.append(f"тернарный оператор: +1 (условие)")

                elif struct == 'nested':
                    nesting_level += 1

                elif struct == 'end_block':
                    if nesting_level > 0:
                        nesting_level -= 1

                elif struct == 'recursion':
                    line_score += 1
                    details.append(f"рекурсия: +1 (сложность понимания)")

        # Проверка макросов препроцессора
        if line.startswith('#'):
            line_score += 1
            details.append("макрос препроцессора: +1")

        # Проверка сложных выражений с несколькими операторами
        if len(re.findall(r'[+\-*/%=&|^<>!]=', line)) > 1:
            line_score += 1
            details.append("множественные операторы: +1")

        total_score += line_score

        line_analysis.append({
            'line_number': line_num,
            'line_content': line,
            'score': line_score,
            'details': details if details else ["нет увеличения сложности"],
            'nesting_level': current_nesting
        })

    return total_score, line_analysis


def export_to_json(total_score: int, line_analysis: List[Dict], filename: str):
    """Экспортирует результаты анализа в JSON файл."""
    result = {
        "total_cognitive_complexity": total_score,
        "interpretation": get_complexity_interpretation(total_score),
        "lines_analyzed": len(line_analysis),
        "line_analysis": line_analysis
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def export_to_xml(total_score: int, line_analysis: List[Dict], filename: str):
    """Экспортирует результаты анализа в XML файл."""
    root = ET.Element("cognitive_complexity_analysis")

    # Summary information
    summary = ET.SubElement(root, "summary")
    ET.SubElement(summary, "total_score").text = str(total_score)
    ET.SubElement(summary, "interpretation").text = get_complexity_interpretation(total_score)
    ET.SubElement(summary, "lines_analyzed").text = str(len(line_analysis))

    # Detailed analysis
    lines_elem = ET.SubElement(root, "lines")
    for analysis in line_analysis:
        line_elem = ET.SubElement(lines_elem, "line")
        ET.SubElement(line_elem, "number").text = str(analysis['line_number'])
        ET.SubElement(line_elem, "content").text = analysis['line_content']
        ET.SubElement(line_elem, "score").text = str(analysis['score'])
        ET.SubElement(line_elem, "nesting_level").text = str(analysis['nesting_level'])

        details_elem = ET.SubElement(line_elem, "details")
        for detail in analysis['details']:
            ET.SubElement(details_elem, "detail").text = detail

    # Format and save
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)


def get_complexity_interpretation(score: int) -> str:
    """Возвращает интерпретацию оценки сложности."""
    if score <= 10:
        return "Низкая сложность - код легко понимается"
    elif score <= 20:
        return "Умеренная сложность - код требует некоторого внимания"
    elif score <= 30:
        return "Высокая сложность - код сложен для понимания"
    else:
        return "Очень высокая сложность - требуется рефакторинг"


def print_analysis(total_score: int, line_analysis: List[Dict]):
    """Выводит результаты анализа в читаемом формате."""
    print(f"Общая когнитивная сложность: {total_score}")
    print(f"Интерпретация: {get_complexity_interpretation(total_score)}")
    print("\nДетальный анализ по строкам:")
    print("=" * 80)

    for analysis in line_analysis:
        if analysis['score'] > 0:
            print(f"Строка {analysis['line_number']} (вложенность: {analysis['nesting_level']}):")
            print(f"  Код: {analysis['line_content']}")
            print(f"  Сложность: +{analysis['score']}")
            for detail in analysis['details']:
                print(f"    - {detail}")
            print("-" * 40)


# Пример использования
if __name__ == "__main__":
    # Пример кода на C для тестирования
    c_code_example = """
    int sumOfPrimes(int max) {
        int total = 0;
        int popugai = 11;
        for (int i = 1; i <= max; i ++) {
            for (int j = 2; j < 2; ++j) {
                if (i % 2 == 0) {
                    cout += 1;
                }
            }
            popugai += i;
            }
        return cout + popugai;
    }
"""

    # Анализ сложности
    total_score, analysis = analyze_cognitive_complexity(c_code_example)

    # Вывод результатов
    print_analysis(total_score, analysis)

    # Экспорт в файлы
    export_to_json(total_score, analysis, "cognitive_complexity.json")
    export_to_xml(total_score, analysis, "cognitive_complexity.xml")

    print("Результаты экспортированы в JSON и XML форматы")