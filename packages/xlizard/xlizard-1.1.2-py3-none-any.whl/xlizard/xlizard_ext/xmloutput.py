# xmloutput.py
'''
Thanks for Holy Wen from Nokia Siemens Networks to let me use his code
to put the result into xml file that is compatible with cppncss.
Jenkins has plugin for cppncss format result to display the diagram.
'''

import os
import re
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics, FileAnalyzer, Config


def xml_output(all_result, verbose):
    """Generate extended XML report with SourceMonitor metrics"""
    result = all_result.result
    import xml.dom.minidom

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "xlizard_metrics", None)
    root = doc.documentElement

    # Get SourceMonitor metrics - рекурсивный поиск файлов
    sm_metrics = {}
    if result and result[0].filename:
        try:
            # Получаем корневую директорию из первого файла
            project_root = os.path.dirname(result[0].filename)
            if verbose:
                print(f"Analyzing directory: {project_root}", file=__import__('sys').stderr)
            
            # Рекурсивно ищем все C/C++ файлы
            all_files = _find_all_source_files(project_root)
            if verbose:
                print(f"Found {len(all_files)} source files for analysis", file=__import__('sys').stderr)
            
            # Анализируем каждый файл
            for file_path in all_files:
                try:
                    metrics = FileAnalyzer.analyze(file_path)
                    if metrics:
                        # Нормализуем путь для consistent поиска
                        rel_path = os.path.relpath(file_path, project_root)
                        sm_metrics[file_path] = metrics
                        sm_metrics[rel_path] = metrics
                        sm_metrics[os.path.basename(file_path)] = metrics
                        if verbose:
                            print(f"Analyzed: {file_path}", file=__import__('sys').stderr)
                except Exception as e:
                    if verbose:
                        print(f"Error analyzing {file_path}: {e}", file=__import__('sys').stderr)
                        
        except Exception as e:
            if verbose:
                print(f"Warning: SourceMonitor metrics analysis failed: {e}", file=__import__('sys').stderr)

    # Create files section
    files_element = doc.createElement("files")
    root.appendChild(files_element)

    for source_file in result:
        if source_file and source_file.filename:
            # Get SourceMonitor metrics for this file - улучшенный поиск
            file_key = os.path.normpath(source_file.filename)
            file_sm_metrics = None
            
            # Пробуем разные варианты поиска
            search_keys = [
                file_key,
                os.path.basename(file_key),
                os.path.abspath(file_key),
                os.path.relpath(file_key) if os.path.isabs(file_key) else file_key
            ]
            
            for key in search_keys:
                if key in sm_metrics:
                    file_sm_metrics = sm_metrics[key]
                    break
                # Также пробуем поиск по частичному совпадению
                elif any(key.endswith(k) for k in sm_metrics.keys() if isinstance(k, str)):
                    for sm_key in sm_metrics.keys():
                        if isinstance(sm_key, str) and key.endswith(sm_key):
                            file_sm_metrics = sm_metrics[sm_key]
                            break

            file_element = doc.createElement("file")
            file_element.setAttribute("name", os.path.basename(source_file.filename))
            file_element.setAttribute("path", source_file.filename)
            files_element.appendChild(file_element)

            # Calculate max metrics for the file
            if source_file.function_list:
                # Initialize max values
                max_nloc = 0
                max_ccn = 0
                max_token_count = 0
                max_parameter_count = 0
                max_func = len(source_file.function_list)  # Количество функций в файле
                max_comment_percentage = "none"
                max_block_depth = "none"
                max_pointer_operations = "none"
                max_preprocessor_directives = "none"

                # First try to get file-level metrics from SourceMonitor
                if file_sm_metrics:
                    max_comment_percentage = file_sm_metrics.get('comment_percentage', "none")
                    max_block_depth = file_sm_metrics.get('max_block_depth', "none")
                    max_pointer_operations = file_sm_metrics.get('pointer_operations', "none")
                    max_preprocessor_directives = file_sm_metrics.get('preprocessor_directives', "none")
                else:
                    # If no SourceMonitor metrics, try to analyze the file directly
                    try:
                        direct_metrics = FileAnalyzer.analyze(source_file.filename)
                        if direct_metrics:
                            max_comment_percentage = direct_metrics.get('comment_percentage', "none")
                            max_block_depth = direct_metrics.get('max_block_depth', "none")
                            max_pointer_operations = direct_metrics.get('pointer_operations', "none")
                            max_preprocessor_directives = direct_metrics.get('preprocessor_directives', "none")
                    except Exception as e:
                        if verbose:
                            print(f"Warning: Direct analysis failed for {source_file.filename}: {e}", file=__import__('sys').stderr)

                # Calculate function-level metrics for basic xlizard metrics
                for func in source_file.function_list:
                    # Basic function metrics
                    max_nloc = max(max_nloc, func.nloc)
                    max_ccn = max(max_ccn, func.cyclomatic_complexity)
                    max_token_count = max(max_token_count, func.token_count)
                    max_parameter_count = max(max_parameter_count, func.parameter_count)

                # Add max metrics to XML
                _add_text_element(doc, file_element, "max_nloc", str(max_nloc))
                _add_text_element(doc, file_element, "max_ccn", str(max_ccn))
                _add_text_element(doc, file_element, "max_token_count", str(max_token_count))
                _add_text_element(doc, file_element, "max_parameter_count", str(max_parameter_count))
                _add_text_element(doc, file_element, "max_func", str(max_func))
                _add_text_element(doc, file_element, "max_comment_percentage", str(max_comment_percentage))
                _add_text_element(doc, file_element, "max_block_depth", str(max_block_depth))
                _add_text_element(doc, file_element, "max_pointer_operations", str(max_pointer_operations))
                _add_text_element(doc, file_element, "max_preprocessor_directives", str(max_preprocessor_directives))
            else:
                # If no functions, use file-level metrics if available
                if file_sm_metrics:
                    max_comment_percentage = file_sm_metrics.get('comment_percentage', "none")
                    max_block_depth = file_sm_metrics.get('max_block_depth', "none")
                    max_pointer_operations = file_sm_metrics.get('pointer_operations', "none")
                    max_preprocessor_directives = file_sm_metrics.get('preprocessor_directives', "none")
                else:
                    # Try direct analysis
                    try:
                        direct_metrics = FileAnalyzer.analyze(source_file.filename)
                        if direct_metrics:
                            max_comment_percentage = direct_metrics.get('comment_percentage', "none")
                            max_block_depth = direct_metrics.get('max_block_depth', "none")
                            max_pointer_operations = direct_metrics.get('pointer_operations', "none")
                            max_preprocessor_directives = direct_metrics.get('preprocessor_directives', "none")
                        else:
                            max_comment_percentage = "none"
                            max_block_depth = "none"
                            max_pointer_operations = "none"
                            max_preprocessor_directives = "none"
                    except Exception as e:
                        if verbose:
                            print(f"Warning: Direct analysis failed for {source_file.filename}: {e}", file=__import__('sys').stderr)
                        max_comment_percentage = "none"
                        max_block_depth = "none"
                        max_pointer_operations = "none"
                        max_preprocessor_directives = "none"

                _add_text_element(doc, file_element, "max_nloc", "0")
                _add_text_element(doc, file_element, "max_ccn", "0")
                _add_text_element(doc, file_element, "max_token_count", "0")
                _add_text_element(doc, file_element, "max_parameter_count", "0")
                _add_text_element(doc, file_element, "max_func", "0")
                _add_text_element(doc, file_element, "max_comment_percentage", str(max_comment_percentage))
                _add_text_element(doc, file_element, "max_block_depth", str(max_block_depth))
                _add_text_element(doc, file_element, "max_pointer_operations", str(max_pointer_operations))
                _add_text_element(doc, file_element, "max_preprocessor_directives", str(max_preprocessor_directives))

    return doc.toprettyxml()


def _find_all_source_files(directory):
    """Рекурсивно найти все C/C++ файлы в директории"""
    source_files = []
    exclude_dirs = {'.git', 'venv', '__pycache__', 'include', 'lib', 'bin'}
    
    try:
        for root, dirs, files in os.walk(directory):
            # Исключаем ненужные директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if os.path.splitext(file)[1].lower() in {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hxx'}:
                    full_path = os.path.join(root, file)
                    source_files.append(full_path)
    except Exception as e:
        print(f"Error walking directory {directory}: {e}", file=__import__('sys').stderr)
    
    return source_files


def _add_text_element(doc, parent, name, value):
    """Helper to add text element"""
    element = doc.createElement(name)
    text = doc.createTextNode(str(value))
    element.appendChild(text)
    parent.appendChild(element)


def _get_function_code(file_path, start_line, end_line):
    """Get source code for a function with encoding support"""
    try:
        # Try multiple encodings
        encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    lines = f.readlines()
                    # Adjust line numbers if they are out of bounds
                    start = max(0, start_line - 1)
                    end = min(len(lines), end_line)
                    
                    if start < end:
                        return ''.join(lines[start:end])
                    else:
                        # If line numbers are invalid, return the whole file
                        return ''.join(lines)
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try binary read with fallback decoding
        with open(file_path, 'rb') as f:
            binary_content = f.read()
            try:
                content = binary_content.decode('utf-8', errors='ignore')
                lines = content.split('\n')
                start = max(0, start_line - 1)
                end = min(len(lines), end_line)
                
                if start < end:
                    return '\n'.join(lines[start:end])
                else:
                    return content
            except:
                return ""
                
    except Exception as e:
        print(f"Error reading function code from {file_path}: {e}", file=__import__('sys').stderr)
        return ""


# ... (остальной код файла остается без изменений, включая функции cppncss_xml_output и другие)

def _get_function_by_content(file_path, encoding):
    """Fallback method to get function content by searching for patterns"""
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
            # Simple pattern matching for function content
            # This is a fallback when line numbers don't match
            lines = content.split('\n')
            if len(lines) > 10:  # Ensure we have some content
                return '\n'.join(lines[:min(50, len(lines))])  # Return first 50 lines as fallback
            return content
    except:
        return ""


def _calculate_function_metrics(func_code):
    """Calculate SourceMonitor metrics for a function"""
    try:
        if not func_code or func_code.strip() == "":
            return {
                'comment_percentage': "none",
                'max_block_depth': "none",
                'pointer_operations': "none"
            }
            
        # Use the same method as FileAnalyzer for consistency
        content_no_strings = FileAnalyzer._remove_comments_and_strings(func_code)
        total_lines = len(func_code.split('\n'))
        comment_lines = FileAnalyzer._count_comments(func_code)
        
        # Calculate block depth using the same method as FileAnalyzer
        max_block_depth = FileAnalyzer._calculate_block_depth(content_no_strings, is_function=True)
        
        # Count pointer operations
        pointer_ops = content_no_strings.count('*') + content_no_strings.count('&')
        
        return {
            'comment_percentage': (comment_lines / total_lines * 100) if total_lines else 0,
            'max_block_depth': max_block_depth,
            'pointer_operations': pointer_ops
        }
    except Exception as e:
        print(f"Error calculating function metrics: {e}", file=__import__('sys').stderr)
        return {
            'comment_percentage': "none",
            'max_block_depth': "none",
            'pointer_operations': "none"
        }


def _count_preprocessor_directives(code):
    """Count preprocessor directives in function code"""
    try:
        if not code or code.strip() == "":
            return "none"
            
        lines = code.split('\n')
        pp_directives = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                pp_directives += 1
        return pp_directives
    except Exception:
        return "none"


# Keep original cppncss compatible output for backward compatibility
def cppncss_xml_output(all_result, verbose):
    """Original cppncss compatible XML output"""
    result = all_result.result
    import xml.dom.minidom

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "cppncss", None)
    root = doc.documentElement

    processing_instruction = doc.createProcessingInstruction(
        'xml-stylesheet',
        'type="text/xsl" ' +
        'href="https://raw.githubusercontent.com' +
        '/terryyin/xlizard/master/xlizard.xsl"')
    doc.insertBefore(processing_instruction, root)

    root.appendChild(_create_function_measure(doc, result, verbose))
    root.appendChild(_create_file_measure(doc, result, all_result))

    return doc.toprettyxml()


def _create_function_measure(doc, result, verbose):
    measure = doc.createElement("measure")
    measure.setAttribute("type", "Function")
    measure.appendChild(_create_labels(doc, ["Nr.", "NCSS", "CCN"]))

    number = 0
    total_func_ncss = 0
    total_func_ccn = 0

    for source_file in result:
        if source_file:
            file_name = source_file.filename
            for func in source_file.function_list:
                number += 1
                total_func_ncss += func.nloc
                total_func_ccn += func.cyclomatic_complexity
                measure.appendChild(
                    _create_function_item(
                        doc, number, file_name, func, verbose))

            if number != 0:
                measure.appendChild(
                    _create_labeled_value_item(
                        doc, 'average', "NCSS", str(total_func_ncss / number)))
                measure.appendChild(
                    _create_labeled_value_item(
                        doc, 'average', "CCN", str(total_func_ccn / number)))
    return measure


def _create_file_measure(doc, result, all_result):
    all_in_one = all_result.as_fileinfo()
    measure = doc.createElement("measure")
    measure.setAttribute("type", "File")
    measure.appendChild(
        _create_labels(doc, ["Nr.", "NCSS", "CCN", "Functions"]))

    file_nr = 0
    file_total_ccn = 0
    file_total_funcs = 0

    for source_file in result:
        file_nr += 1
        file_total_ccn += source_file.CCN
        file_total_funcs += len(source_file.function_list)
        measure.appendChild(
            _create_file_node(doc, source_file, file_nr))

    if file_nr != 0:
        file_summary = [("NCSS", all_in_one.nloc / file_nr),
                        ("CCN", file_total_ccn / file_nr),
                        ("Functions", file_total_funcs / file_nr)]
        for key, val in file_summary:
            measure.appendChild(
                _create_labeled_value_item(doc, 'average', key, val))

    summary = [("NCSS", all_in_one.nloc),
               ("CCN", file_total_ccn),
               ("Functions", file_total_funcs)]
    for key, val in summary:
        measure.appendChild(_create_labeled_value_item(doc, 'sum', key, val))

    if file_total_funcs != 0:
        summary = [("NCSS", all_in_one.average_nloc),
                   ("CCN", all_in_one.average_cyclomatic_complexity)]
        for key, val in summary:
            measure.appendChild(_create_labeled_value_item(
                doc, 'average', key, val))

    return measure


def _create_label(doc, name):
    label = doc.createElement("label")
    text1 = doc.createTextNode(name)
    label.appendChild(text1)
    return label


def _create_labels(doc, label_name):
    labels = doc.createElement("labels")
    for label in label_name:
        labels.appendChild(_create_label(doc, label))

    return labels


def _create_function_item(doc, number, file_name, func, verbose):
    item = doc.createElement("item")
    if verbose:
        item.setAttribute(
            "name", "%s at %s:%s" %
            (func.long_name, file_name, func.start_line))
    else:
        item.setAttribute(
            "name", "%s(...) at %s:%s" %
            (func.name, file_name, func.start_line))
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(number))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(func.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(func.cyclomatic_complexity))
    value3.appendChild(text3)
    item.appendChild(value3)
    return item


def _create_labeled_value_item(doc, name, label, value):
    average_ncss = doc.createElement(name)
    average_ncss.setAttribute("label", label)
    average_ncss.setAttribute("value", str(value))
    return average_ncss


def _create_file_node(doc, source_file, file_nr):
    item = doc.createElement("item")
    item.setAttribute("name", source_file.filename)
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(file_nr))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(source_file.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(source_file.CCN))
    value3.appendChild(text3)
    item.appendChild(value3)
    value4 = doc.createElement("value")
    text4 = doc.createTextNode(str(len(source_file.function_list)))
    value4.appendChild(text4)
    item.appendChild(value4)
    return item