class Node:
    def __init__(self):
        self.children = {}    # Дочерние узлы (ключ - символ, значение - узел)
        self.fail = None      # Суффиксная ссылка (fail link)
        self.output = []      # Список шаблонов, которые заканчиваются в этом узле
        self.output_link = None  # Явная выходная ссылка (пока не используем)

class AhoKorasik:
    def __init__(self):
        """Инициализация автомата с корнем"""
        self.root = Node()
        self.node_counter = 0

    def add_pattern(self, pattern, index):
        """Добавление одного шаблона в дерево"""
        print(f"Добавляем шаблон '{pattern}' с номером {index}")
        node = self.root
        for char in pattern:
            if char not in node.children:
                self.node_counter += 1
                node.children[char] = Node()
                print(f"  Создаём новый узел для символа '{char}'")
            else:
                print(f"  Переходим в существующий узел для символа '{char}'")
            node = node.children[char]
        node.output.append((index, len(pattern)))
        print(f"  Шаблон '{pattern}' завершён в текущем узле.\n")

    def build_fail_links(self):
        """Построение суффиксных ссылок"""
        from collections import deque
        queue = deque()

        print("Строим суффиксные ссылки (fail links)...")
        # Инициализация: дочерние узлы корня получают fail-ссылку на корень
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        # Проход в ширину по всем узлам
        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                print(f"  Обрабатываем переход по символу '{char}'")
                fail_node = current_node.fail

                # Поднимаемся по fail-ссылкам, пока не найдём символ или не дойдём до корня
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail

                if fail_node:
                    child_node.fail = fail_node.children[char]
                    print(f"    Устанавливаем fail-ссылку на узел с символом '{char}'")
                else:
                    child_node.fail = self.root
                    print(f"    Устанавливаем fail-ссылку на корень")

                # Наследуем выходные шаблоны
                child_node.output += child_node.fail.output

                queue.append(child_node)
        print("Суффиксные ссылки построены.\n")

    def search(self, text):
        """Поиск всех вхождений шаблонов в тексте"""
        print(f"Начинаем поиск в тексте: '{text}'")
        node = self.root
        matches = []

        for i, char in enumerate(text):
            print(f"\nОбрабатываем символ '{char}' (позиция {i+1})")
            # Если нет перехода по символу - идём по fail-ссылкам
            while node != self.root and char not in node.children:
                print(f"  Нет перехода по '{char}', следуем по fail-ссылке")
                node = node.fail

            if char in node.children:
                node = node.children[char]
                print(f"  Переход по символу '{char}' успешен")
            else:
                node = self.root
                print(f"  Переход по символу '{char}' не найден, возвращаемся в корень")

            # Если есть выходы (output), значит нашли шаблоны
            for pattern_index, pattern_len in node.output:
                start_pos = i - pattern_len + 2  # Позиция старта в 1-based индексации
                print(f"  Найдено совпадение: шаблон {pattern_index} на позиции {start_pos}")
                matches.append((start_pos, pattern_index))

        print("\nПоиск завершён.\n")
        return matches

    def compute_chain_lengths(self):
        """Вычисление максимальных длин цепочек суффиксных и конечных ссылок"""
        print("\n" + "="*50)
        print("Подробный анализ длин цепочек ссылок...")
        print("="*50 + "\n")
        
        nodes = []
        def collect_nodes(node):
            nodes.append(node)
            for child in node.children.values():
                collect_nodes(child)
        collect_nodes(self.root)

        # Вычисляем максимальную длину цепочки по fail-ссылкам
        max_fail_length = 0
        fail_chains = []
        
        for node in nodes:
            if node == self.root:
                continue
            length = 0
            current = node
            chain_nodes = [current]
            while current != self.root and current.fail:
                length += 1
                current = current.fail
                chain_nodes.append(current)
            
            if length > 0:
                # Получаем символы для идентификации узлов
                chain_info = []
                for n in chain_nodes[:-1]:  # Исключаем корень из вывода
                    # Находим символ(ы) перехода к этому узлу
                    chars = []
                    for parent in nodes:
                        for char, child in parent.children.items():
                            if child == n:
                                chars.append(char)
                    if chars:
                        chain_info.append(f"'{''.join(chars)}'")
                    else:
                        chain_info.append("(root)")
                
                fail_chains.append((length, chain_info))
                max_fail_length = max(max_fail_length, length)

        # Сортируем цепочки по длине для наглядности
        fail_chains.sort(reverse=True, key=lambda x: x[0])
        
        print("\nЦепочки суффиксных (fail) ссылок:")
        if not fail_chains:
            print("  Нет цепочек длиннее 1")
        else:
            for length, chain in fail_chains:
                print(f"  Длина {length}: {' -> '.join(chain)}")

        # Вычисляем максимальную длину цепочки по выходным ссылкам
        max_output_length = 0
        output_chains = []
        
        for node in nodes:
            if node.output:
                length = 1  # сам узел считается
                current = node.fail
                chain_nodes = [node]
                while current != self.root:
                    if current.output:
                        length += 1
                        chain_nodes.append(current)
                    current = current.fail
                
                if length > 1:
                    # Получаем информацию о шаблонах в цепочке
                    patterns_info = []
                    for n in chain_nodes:
                        patterns = [f"'{pat[0]}' (длина {pat[1]})" for pat in n.output]
                        patterns_info.append(f"[{', '.join(patterns)}]")
                    
                    output_chains.append((length, patterns_info))
                    max_output_length = max(max_output_length, length)

        # Сортируем цепочки по длине
        output_chains.sort(reverse=True, key=lambda x: x[0])
        
        print("\nЦепочки выходных (output) ссылок:")
        if not output_chains:
            print("  Нет цепочек длиннее 1")
        else:
            for length, chain in output_chains:
                print(f"  Длина {length}: {' -> '.join(chain)}")

        print("\n" + "="*50)
        print("Итоговые максимальные длины цепочек:")
        print(f"Максимальная длина цепочки суффиксных (fail) ссылок: {max_fail_length}")
        print(f"Максимальная длина цепочки выходных (output) ссылок: {max_output_length}")
        print("="*50 + "\n")

def main():
    """Основная функция"""
    print("="*50)
    print("Алгоритм Ахо-Корасик")
    print("Введите:")
    print("1. Текст для поиска")
    print("2. Количество шаблонов")
    print("3. Список шаблонов (по одному в строке)")
    print("="*50 + "\n")

    # Ввод текста и шаблонов
    text = input("Введите текст: ").strip()
    n = int(input("Введите количество шаблонов: "))
    patterns = []
    for i in range(n):
        pattern = input(f"Введите шаблон {i+1}: ").strip()
        patterns.append(pattern)

    # Построение автомата
    ak = AhoKorasik()
    for i, pattern in enumerate(patterns, 1):
        ak.add_pattern(pattern, i)

    ak.build_fail_links()

    # Поиск шаблонов в тексте
    matches = ak.search(text)

    print("\n" + "="*50)
    print("Результаты поиска:")
    if not matches:
        print("Совпадений не найдено")
    else:
        for pos, pat_num in sorted(matches):
            print(f"Позиция {pos}: шаблон {pat_num} ('{patterns[pat_num-1]}')")
    print("="*50)

    # Анализ длин цепочек
    ak.compute_chain_lengths()

if __name__ == "__main__":
    main()
