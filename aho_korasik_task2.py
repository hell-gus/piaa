import sys
from collections import deque

class Node:
    def __init__(self):
        self.children = {}
        self.fail = None
        self.output = []  # хранит пары (индекс подшаблона, длина подшаблона)

class AhoCorasick:
    def __init__(self):
        self.root = Node()
        self.nodes = [self.root]  # для хранения всех узлов

    def add_pattern(self, pattern, index, length):
        node = self.root
        for char in pattern:
            if char not in node.children:
                new_node = Node()
                node.children[char] = new_node
                self.nodes.append(new_node)  # добавляем узел в общий список
            node = node.children[char]
        node.output.append((index, length))

    def build_failure_links(self):
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
                if fail_node is None:
                    child_node.fail = self.root
                else:
                    child_node.fail = fail_node.children.get(char, self.root)
                child_node.output += child_node.fail.output
                queue.append(child_node)

    def search(self, text):
        node = self.root
        result = []
        for i in range(len(text)):
            char = text[i]
            while node != self.root and char not in node.children:
                node = node.fail
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root
            for pattern_index, length in node.output:
                result.append((i - length + 1, pattern_index))
        return result
    
    def get_longest_chains(self):
        max_fail_chain = 0
        max_output_chain = 0
        
        for node in self.nodes:
            # Вычисляем длину цепочки fail-ссылок
            fail_chain_length = 0
            current = node
            while current != self.root:
                fail_chain_length += 1
                current = current.fail
            max_fail_chain = max(max_fail_chain, fail_chain_length)
            
            # Вычисляем длину цепочки output-ссылок
            output_chain_length = 0
            current = node
            while current.output:
                output_chain_length += 1
                if current.fail == current or current.fail is None:
                    break
                current = current.fail
            max_output_chain = max(max_output_chain, output_chain_length)
        
        return max_fail_chain, max_output_chain

def find_wildcard_matches(text, pattern, wildcard):
    # Разделяем шаблон на подшаблоны, разделенные wildcard
    subpatterns = []
    current = []
    for char in pattern:
        if char == wildcard:
            if current:
                subpatterns.append(''.join(current))
                current = []
        else:
            current.append(char)
    if current:
        subpatterns.append(''.join(current))

    if not subpatterns:
        return []

    # Создаем автомат Ахо-Корасика для подшаблонов
    ac = AhoCorasick()
    for i, subpattern in enumerate(subpatterns):
        ac.add_pattern(subpattern, i + 1, len(subpattern))
    ac.build_failure_links()

    # Ищем все вхождения подшаблонов
    matches = ac.search(text)
    subpattern_positions = [[] for _ in range(len(subpatterns))]
    for pos, subpat_idx in matches:
        subpattern_positions[subpat_idx - 1].append(pos)

    # Теперь проверяем, что подшаблоны расположены правильно с учетом wildcard
    pattern_length = len(pattern)
    text_length = len(text)
    result = set()

    # Для каждого подшаблона проверяем возможные позиции
    for i in range(len(subpatterns)):
        subpat = subpatterns[i]
        subpat_len = len(subpat)
        for pos in subpattern_positions[i]:
            # Проверяем, что перед подшаблоном и после него есть место для wildcard
            # и что wildcard и подшаблоны соответствуют шаблону
            start_in_pattern = pattern.find(subpat)
            start_in_text = pos
            global_start = start_in_text - start_in_pattern
            if global_start < 0:
                continue
            global_end = global_start + pattern_length
            if global_end > text_length:
                continue
            # Проверяем, что символы в тексте соответствуют шаблону
            match = True
            for j in range(pattern_length):
                pattern_char = pattern[j]
                if pattern_char == wildcard:
                    continue
                text_char = text[global_start + j]
                if pattern_char != text_char:
                    match = False
                    break
            if match:
                result.add(global_start + 1)  # +1 для 1-based индексации

    return sorted(result)

def main():
    text = sys.stdin.readline().strip()
    pattern = sys.stdin.readline().strip()
    wildcard = sys.stdin.readline().strip()
    matches = find_wildcard_matches(text, pattern, wildcard)
    for pos in matches:
        print(pos)

if __name__ == "__main__":
    main()
