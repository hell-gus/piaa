import sys
from collections import deque

# Класс, представляющий узел в дереве автомата Ахо-Корасик
class Node:
    def __init__(self):
        # Дочерние узлы (ключ - символ, значение - узел)
        self.children = {}
        # Ссылка на узел, представляющий самый длинный суффикс текущего префикса
        self.fail = None
        # Список для хранения индексов подшаблонов, заканчивающихся в этом узле, и их длин
        self.output = []

# Класс автомата Ахо-Корасик
class AhoCorasick:
    def __init__(self):
        # Корневой узел дерева
        self.root = Node()

    # Метод для добавления подшаблона в дерево
    def add_pattern(self, pattern, index, length):
        node = self.root
        for char in pattern:
            # Создаем дочерний узел, если символ отсутствует
            if char not in node.children:
                node.children[char] = Node()
            node = node.children[char]
        # Добавляем информацию о подшаблоне (индекс и длину) в конечный узел
        node.output.append((index, length))

    # Метод для построения fail-ссылок и объединения выходов
    def build_failure_links(self):
        queue = deque()
        # Инициализация fail-ссылок для детей корня
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        # Обработка узлов в порядке BFS для построения fail-ссылок
        while queue:
            current_node = queue.popleft()
            # Обработка каждого дочернего узла текущего узла
            for char, child_node in current_node.children.items():
                # Начинаем с fail-ссылки текущего узла
                fail_node = current_node.fail
                # Ищем самый длинный суффикс, который есть в дереве
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail
                # Устанавливаем fail-ссылку для дочернего узла
                child_node.fail = fail_node.children[char] if fail_node else self.root
                # Объединяем выходы текущего узла и его fail-ссылки
                child_node.output += child_node.fail.output
                queue.append(child_node)

    # Метод для поиска всех вхождений подшаблонов в тексте
    def search(self, text):
        node = self.root
        result = []
        for i, char in enumerate(text):
            # Переходим по fail-ссылкам, пока не найдем подходящий символ или не вернемся в корень
            while node != self.root and char not in node.children:
                node = node.fail
            # Переходим к дочернему узлу, если символ найден
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root  # Остаемся в корне, если символ не найден
            # Добавляем все найденные подшаблоны для текущей позиции
            for pattern_index, length in node.output:
                result.append((i - length + 1, pattern_index))
        return result

# Функция для поиска вхождений шаблона с джокерами в тексте
def find_wildcard_matches(text, pattern, wildcard):
    # Разделение шаблона на подшаблоны по символу-джокеру
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

    # Обработка случая, когда шаблон состоит только из джокеров
    if not subpatterns:
        return []

    # Инициализация автомата и добавление подшаблонов
    ac = AhoCorasick()
    for i, subpattern in enumerate(subpatterns):
        ac.add_pattern(subpattern, i + 1, len(subpattern))
    ac.build_failure_links()

    # Поиск всех вхождений подшаблонов в тексте
    matches = ac.search(text)
    # Группировка позиций по индексам подшаблонов
    subpattern_positions = [[] for _ in range(len(subpatterns))]
    for pos, subpat_idx in matches:
        subpattern_positions[subpat_idx - 1].append(pos)

    # Поиск полных совпадений исходного шаблона с учетом джокеров
    result = set()
    pattern_length = len(pattern)
    text_length = len(text)

    # Проверка каждого возможного положения подшаблонов
    for i in range(len(subpatterns)):
        subpat_len = len(subpatterns[i])
        for pos in subpattern_positions[i]:
            # Вычисление предполагаемой стартовой позиции всего шаблона
            start_in_pattern = pattern.find(subpatterns[i])
            global_start = pos - start_in_pattern
            # Проверка границ текста
            if global_start < 0 or (global_start + pattern_length) > text_length:
                continue
            # Проверка соответствия всех символов шаблона (с учетом джокеров)
            valid = True
            for j in range(pattern_length):
                if pattern[j] == wildcard:
                    continue
                if text[global_start + j] != pattern[j]:
                    valid = False
                    break
            if valid:
                # Добавление позиции в 1-индексации
                result.add(global_start + 1)

    return sorted(result)

def main():
    print("Введите текст:")
    text = sys.stdin.readline().strip()
    print("Введите шаблон:")
    pattern = sys.stdin.readline().strip()
    print("Введите символ-джокер:")
    wildcard = sys.stdin.readline().strip()
    matches = find_wildcard_matches(text, pattern, wildcard)
    for pos in matches:
        print(pos)

if __name__ == "__main__":
    main()
