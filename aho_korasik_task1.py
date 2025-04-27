class Node:
    def __init__(self):
        self.children = {}    # Дочерние узлы (ключ - символ, значение - узел)
        self.fail = None      # Суффиксная ссылка (fail link)
        self.output = []      # Выходные ссылки (номера шаблонов, заканчивающихся здесь)
        self.output_link = None  # Явная выходная ссылка (для расширенного функционала)

class AhoKorasik:
    def __init__(self):
        """Инициализация автомата с корневым узлом"""
        self.root = Node()
        self.node_counter = 0  # Счетчик для идентификации узлов

    def add_pattern(self, pattern, index):
        """Добавление шаблона в бор"""
        node = self.root
        for char in pattern:
            if char not in node.children:
                self.node_counter += 1
                node.children[char] = Node()
            node = node.children[char]
        # Сохраняем индекс шаблона и его длину
        node.output.append((index, len(pattern)))

    def build_fail_links(self):
        """Построение суффиксных ссылок (алгоритм Ахо-Корасик)"""
        from collections import deque
        queue = deque()

        # Инициализация очереди детьми корня
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                # Поиск fail-ссылки для текущего символа
                fail_node = current_node.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail

                if fail_node is None:
                    child_node.fail = self.root
                else:
                    child_node.fail = fail_node.children.get(char, self.root)

                # Наследуем выходные ссылки
                child_node.output += child_node.fail.output
                queue.append(child_node)

    def search(self, text):
        """Поиск всех вхождений шаблонов в тексте"""
        node = self.root
        matches = []

        for i, char in enumerate(text):
            # Переход по fail-ссылкам, если нет перехода по символу
            while node is not self.root and char not in node.children:
                node = node.fail

            if char in node.children:
                node = node.children[char]
            else:
                node = self.root

            # Добавляем все найденные шаблоны
            for pattern_index, pattern_len in node.output:
                start_pos = i - pattern_len + 2  # Позиция начала (1-based)
                matches.append((start_pos, pattern_index))

        return matches

    def format_node_label(self, node):
        """Форматирование метки узла для вывода"""
        if node == self.root:
            return "корень"
        return f"узел (id: {id(node) % 1000})"

    def compute_chain_lengths(self):
        """Анализ длин цепочек суффиксных и выходных ссылок"""
        print("\n=== Анализ длин цепочек ссылок ===")
        
        # Сбор всех узлов бора
        nodes = []
        def collect_nodes(node):
            nodes.append(node)
            for child in node.children.values():
                collect_nodes(child)
        collect_nodes(self.root)

        # Анализ fail-ссылок
        max_fail_chain = 0
        max_fail_path = []
        print("\nАнализ fail-ссылок:")

        for node in nodes:
            if node != self.root and node.fail is not None:
                chain = [self.format_node_label(node)]
                current = node.fail
                length = 1

                while current != self.root and current is not None:
                    chain.append(self.format_node_label(current))
                    current = current.fail
                    length += 1

                chain.append("корень")
                print(f"  {self.format_node_label(node)}: {' -> '.join(chain)}, длина = {length}")

                if length > max_fail_chain:
                    max_fail_chain = length
                    max_fail_path = chain

        # Анализ output-ссылок
        max_output_chain = 0
        max_output_path = []
        print("\nАнализ output-ссылок:")

        for node in nodes:
            if hasattr(node, 'output_link') and node.output_link is not None:
                chain = [self.format_node_label(node)]
                current = node.output_link
                length = 1

                while current is not None and hasattr(current, 'output_link'):
                    chain.append(self.format_node_label(current))
                    current = current.output_link
                    length += 1

                print(f"  {self.format_node_label(node)}: {' -> '.join(chain)}, длина = {length}")

                if length > max_output_chain:
                    max_output_chain = length
                    max_output_path = chain

        # Вывод итогов
        print("\n" + "="*50)
        print("Максимальные длины цепочек:")
        print(f"fail-ссылки: {max_fail_chain} ({' -> '.join(max_fail_path)})" if max_fail_chain > 0 else "fail-ссылки: нет")
        print(f"output-ссылки: {max_output_chain} ({' -> '.join(max_output_path)})" if max_output_chain > 0 else "output-ссылки: нет")
        print("="*50)

def main():
    """Основная функция для работы из командной строки"""
    print("="*50)
    print("Алгоритм Ахо-Корасик")
    print("Введите:")
    print("1. Текст для поиска")
    print("2. Количество шаблонов")
    print("3. Список шаблонов (по одному в строке)")
    print("="*50 + "\n")

    text = input().strip()
    n = int(input())
    patterns = [input().strip() for _ in range(n)]
    
    # Инициализация и построение автомата
    ak = AhoKorasik()
    for i, pattern in enumerate(patterns, 1):
        ak.add_pattern(pattern, i)
    
    ak.build_fail_links()
    
    # Поиск и вывод результатов
    print("\n" + "="*50)
    print("Результаты поиска:")
    matches = ak.search(text)
    if not matches:
        print("Совпадений не найдено")
    else:
        for pos, pat_num in sorted(matches):
            print(f"Позиция {pos}: шаблон {pat_num} ('{patterns[pat_num-1]}')")
    
    # Анализ структуры автомата
    ak.compute_chain_lengths()

if __name__ == "__main__":
    main()
