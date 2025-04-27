class Node:
    def __init__(self):
        self.children = {}    # Дочерние узлы (ключ - символ, значение - узел)
        self.fail = None      # Суффиксная ссылка (fail link)
        self.output = []      # Выходные ссылки (номера шаблонов, заканчивающихся здесь)
        self.output_link = None  # Явная выходная ссылка (можно будет использовать)

class AhoKorasik:
    def __init__(self):
        self.root = Node()
        self.node_counter = 0

    def add_pattern(self, pattern, index):
        node = self.root
        for char in pattern:
            if char not in node.children:
                self.node_counter += 1
                node.children[char] = Node()
            node = node.children[char]
        node.output.append((index, len(pattern)))

    def build_fail_links(self):
        from collections import deque
        queue = deque()

        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                fail_node = current_node.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail

                child_node.fail = fail_node.children[char] if fail_node and char in fail_node.children else self.root
                child_node.output += child_node.fail.output
                queue.append(child_node)

    def search(self, text):
        node = self.root
        matches = []

        for i, char in enumerate(text):
            while node != self.root and char not in node.children:
                node = node.fail

            node = node.children.get(char, self.root)

            for pattern_index, pattern_len in node.output:
                start_pos = i - pattern_len + 2
                matches.append((start_pos, pattern_index))

        return matches

    def compute_chain_lengths(self):
        """Функция для варианта 3: Вычисляет длины самых длинных цепочек суффиксных и конечных ссылок"""
        nodes = []
        def collect_nodes(node):
            nodes.append(node)
            for child in node.children.values():
                collect_nodes(child)
        collect_nodes(self.root)

        # Суффиксные ссылки (fail-links)
        max_fail_length = 0
        for node in nodes:
            if node == self.root:
                continue
            length = 0
            current = node
            while current != self.root and current.fail:
                length += 1
                current = current.fail
            max_fail_length = max(max_fail_length, length)

        # Конечные ссылки (output-links)
        max_output_length = 0
        for node in nodes:
            if node.output:
                length = 1
                current = node.fail
                while current != self.root:
                    if current.output:
                        length += 1
                    current = current.fail
                max_output_length = max(max_output_length, length)

        print("\n" + "="*50)
        print(f"Максимальная длина цепочки суффиксных ссылок: {max_fail_length}")
        print(f"Максимальная длина цепочки конечных ссылок: {max_output_length}")
        print("="*50)

def main():
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

    ak = AhoKorasik()
    for i, pattern in enumerate(patterns, 1):
        ak.add_pattern(pattern, i)

    ak.build_fail_links()

    print("\n" + "="*50)
    print("Результаты поиска:")
    matches = ak.search(text)
    if not matches:
        print("Совпадений не найдено")
    else:
        for pos, pat_num in sorted(matches):
            print(f"Позиция {pos}: шаблон {pat_num} ('{patterns[pat_num-1]}')")

    # Новая функция из варианта 3
    ak.compute_chain_lengths()

if __name__ == "__main__":
    main()
