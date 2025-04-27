import sys
from collections import deque

class Node:
    """Узел для дерева автомата Ахо-Корасик"""
    def __init__(self):
        self.children = {}    # Дочерние узлы (ключ: символ, значение: узел)
        self.fail = None      # Ссылка на узел с наибольшим суффиксом (fail-ссылка)
        self.output = []      # Список паттернов, заканчивающихся в этом узле (индекс, длина)
        
    def __repr__(self):
        return f"Node(output={self.output}, children={list(self.children.keys())})"

class AhoCorasick:
    """Автомат Ахо-Корасик для множественного поиска подстрок"""
    def __init__(self):
        self.root = Node()
        print("\n=== Инициализация автомата ===")
        print(f"Создан корневой узел: {self.root}")

    def add_pattern(self, pattern, index, length):
        """Добавление подшаблона в дерево"""
        print(f"\nДобавление подшаблона '{pattern}' (индекс {index}, длина {length})")
        node = self.root
        for i, char in enumerate(pattern):
            # Создаем новый узел, если символ отсутствует
            if char not in node.children:
                print(f"  Создание нового узла для символа '{char}'")
                node.children[char] = Node()
            node = node.children[char]
            status = 'последний' if i == len(pattern)-1 else 'промежуточный'
            print(f"  Переход к узлу для '{char}' ({status})")
        # Добавляем информацию о паттерне в конечный узел
        node.output.append((index, length))
        print(f"  Добавлен выходной паттерн {node.output} в конечный узел")

    def build_failure_links(self):
        """Построение fail-ссылок с использованием BFS"""
        print("\n=== Построение fail-ссылок ===")
        queue = deque()
        # Инициализация fail-ссылок для детей корня
        for char, child in self.root.children.items():
            print(f"Инициализация fail-ссылки для корневого ребенка '{char}'")
            child.fail = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()
            print(f"\nОбработка узла {current_node}")
            for char, child in current_node.children.items():
                print(f"\n  Обработка ребенка '{char}'")
                fail_node = current_node.fail
                steps = 0
                
                # Поиск подходящего суффикса
                print(f"  Поиск fail-ссылки для '{char}':")
                while fail_node is not None and char not in fail_node.children:
                    print(f"    Шаг {steps}: переход по fail к {fail_node}")
                    fail_node = fail_node.fail
                    steps += 1

                # Установка fail-ссылки для текущего ребенка
                child.fail = fail_node.children[char] if fail_node else self.root
                print(f"  Установка fail-ссылки: {child.fail}")
                
                # Наследование выходов от fail-узла
                child.output += child.fail.output
                if child.output:
                    print(f"  Объединение выходов: {child.output}")
                
                queue.append(child)
                print(f"  Добавлен в очередь: {child}")

    def search(self, text):
        """Поиск всех подшаблонов в тексте"""
        print(f"\n=== Начало поиска в тексте '{text}' ===")
        node = self.root
        result = []
        for i, char in enumerate(text):
            print(f"\nСимвол [{i}]: '{char}'")
            print(f"Текущий узел до обработки: {node}")
            
            # Переход по fail-ссылкам до нахождения совпадения или корня
            while node != self.root and char not in node.children:
                print(f"  Переход по fail-ссылке: {node} -> {node.fail}")
                node = node.fail

            # Переход к следующему узлу
            if char in node.children:
                node = node.children[char]
                print(f"  Переход к ребенку: {node}")
            else:  # Остаемся в корне, если символ не найден
                print("  Символ не найден, возврат в корень")
                node = self.root
                
            # Собираем все найденные паттерны
            if node.output:
                print(f"  Найдены выходы: {node.output}")
                for pattern_index, length in node.output:
                    pos = i - length + 1
                    print(f"    Запись позиции {pos} для паттерна {pattern_index}")
                    result.append((pos, pattern_index))
        return result

    def collect_all_nodes(self):
        """Сбор всех узлов автомата для анализа"""
        nodes = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            nodes.append(node)
            for child in node.children.values():
                queue.append(child)
        return nodes

    def get_longest_chains(self):
        """Поиск максимальных цепочек fail и output ссылок"""
        print("\n=== Поиск максимальных цепочек ===")
        nodes = self.collect_all_nodes()
        max_fail_chain = 0
        max_output_chain = 0
        
        print(f"Всего узлов в автомате: {len(nodes)}")
        
        for i, node in enumerate(nodes):
            print(f"\nАнализ узла {i + 1}: {node}")
            
            # Анализ fail-цепочки
            fail_chain = []
            current = node
            while current != self.root:
                fail_chain.append(current)
                current = current.fail
            fail_length = len(fail_chain)
            
            print(f"  Fail-цепочка (длина {fail_length}):")
            chain = [f"Узел {i + 1}"] + [f"-> Fail {n}" for n in fail_chain]
            print("   " + " ".join(chain))
            
            if fail_length > max_fail_chain:
                print(f"  Новый максимум fail-цепи: {fail_length}")
                max_fail_chain = fail_length

            # Анализ output-цепочки
            output_chain = []
            current = node
            while current.output or (current.fail and current.fail != current):
                output_chain.append(current)
                current = current.fail
            output_length = len(output_chain)
            
            print(f"  Output-цепочка (длина {output_length}):")
            chain = [f"Узел {i + 1}"] + [f"-> {n}" for n in output_chain[1:]]
            print("   " + " ".join(chain))
            
            if output_length > max_output_chain:
                print(f"  Новый максимум output-цепи: {output_length}")
                max_output_chain = output_length

        print("\nИтоги:")
        print(f"Максимальная длина fail-цепочки: {max_fail_chain}")
        print(f"Максимальная длина output-цепочки: {max_output_chain}")
        return max_fail_chain, max_output_chain

def find_wildcard_matches(text, pattern, wildcard):
    """Поиск шаблонов с джокерами в тексте"""
    print("\n" + "="*50)
    print(f"Начало обработки:\nТекст: '{text}'\nШаблон: '{pattern}'\nДжокер: '{wildcard}'")
    
    # Этап 1: Разделение шаблона на подшаблоны
    print("\n=== Шаг 1: Разделение шаблона на подшаблоны ===")
    subpatterns = []
    current = []
    for char in pattern:
        if char == wildcard:
            if current:
                subpat = ''.join(current)
                subpatterns.append(subpat)
                print(f"Найден подшаблон: '{subpat}'")
                current = []
        else:
            current.append(char)
    if current:
        subpat = ''.join(current)
        subpatterns.append(subpat)
        print(f"Найден подшаблон: '{subpat}'")
    
    print(f"\nИтоговые подшаблоны: {subpatterns}")
    if not subpatterns:
        print("Нет подшаблонов для поиска")
        return []

    # Этап 2: Построение автомата
    print("\n=== Шаг 2: Построение автомата Ахо-Корасик ===")
    ac = AhoCorasick()
    for i, subpattern in enumerate(subpatterns):
        ac.add_pattern(subpattern, i + 1, len(subpattern))
    
    # Этап 3: Построение fail-ссылок
    print("\n=== Шаг 3: Построение fail-ссылок ===")
    ac.build_failure_links()
    
    # Этап 3a: Анализ цепочек
    ac.get_longest_chains()

    # Этап 4: Поиск подшаблонов
    print("\n=== Шаг 4: Поиск подшаблонов в тексте ===")
    matches = ac.search(text)
    print(f"\nВсе совпадения подшаблонов: {matches}")
    
    # Группировка позиций по подшаблонам
    subpattern_positions = [[] for _ in range(len(subpatterns))]
    for pos, subpat_idx in matches:
        subpattern_positions[subpat_idx - 1].append(pos)
    
    # Этап 5: Проверка полных совпадений
    print("\n=== Шаг 5: Поиск полных совпадений с учетом джокеров ===")
    print(f"Позиции подшаблонов: {subpattern_positions}")
    result = set()
    pattern_length = len(pattern)
    text_length = len(text)
    
    for i in range(len(subpatterns)):
        subpat = subpatterns[i]
        print(f"\nПроверка подшаблона {i+1} ('{subpat}'):")
        
        for pos in subpattern_positions[i]:
            # Вычисление предполагаемой стартовой позиции
            start_in_pattern = pattern.find(subpat)
            global_start = pos - start_in_pattern
            global_end = global_start + pattern_length
            
            print(f"\n  Возможное совпадение на позиции {pos}")
            print(f"  Предполагаемый старт в тексте: {global_start}")
            print(f"  Предполагаемый конец в тексте: {global_end}")
            
            # Проверка границ текста
            if global_start < 0:
                print("  Отклонено: старт позиция меньше 0")
                continue
            if global_end > text_length:
                print("  Отклонено: выход за границы текста")
                continue
                
            # Поэлементная проверка совпадения с шаблоном
            valid = True
            print("  Проверка соответствия символов:")
            for j in range(pattern_length):
                text_char = text[global_start + j] if (global_start + j) < text_length else None
                pattern_char = pattern[j]
                
                if pattern_char == wildcard:
                    status = "Джокер - пропуск"
                elif text_char == pattern_char:
                    status = "Совпадение"
                else:
                    status = "Несовпадение"
                    valid = False
                
                print(f"    Позиция {j}: T '{text_char}' vs P '{pattern_char}' - {status}")
                if not valid: break
                    
            if valid:
                print(f"  Полное совпадение! Добавлена позиция {global_start + 1}")
                result.add(global_start + 1)
    
    print("\n=== Итоговые совпадения ===")
    return sorted(result)

def main():
    """Основная функция для ввода/вывода"""
    print("Введите текст:")
    text = sys.stdin.readline().strip()
    print("Введите шаблон:")
    pattern = sys.stdin.readline().strip()
    print("Введите символ-джокер:")
    wildcard = sys.stdin.readline().strip()
    
    print("\n" + "="*50)
    print("Начало выполнения программы")
    matches = find_wildcard_matches(text, pattern, wildcard)
    
    print("\nРезультат:")
    if matches:
        for pos in matches:
            print(f"Совпадение на позиции: {pos}")
    else:
        print("Совпадений не найдено")

if __name__ == "__main__":
    main()
