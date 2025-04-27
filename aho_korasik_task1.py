class Node:
    def __init__(self):
        self.children = {}  # переходы по символам
        self.fail = None    # суффиксная ссылка
        self.output = []    # номера шаблонов, которые заканчиваются здесь

class AchoKarasik:
    def __init__(self):
        self.root = Node()

    def add_pattern(self, pattern, index):
        node = self.root
        for char in pattern:
            if char not in node.children:
                node.children[char] = Node()
            node = node.children[char]
        node.output.append(index)

    def build_faillink(self):
        from collections import deque
        queue = deque()
        
        # Инициализация: все дети root получают fail = root
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()
            
            for char, child_node in current_node.children.items():
                # Находим fail-узел для текущего узла
                fail_node = current_node.fail
                
                # Пока fail_node не None и не имеет перехода по char
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail
                
                if fail_node is None:
                    child_node.fail = self.root
                else:
                    child_node.fail = fail_node.children.get(char, self.root)
                
                # Добавляем output из fail-узла
                child_node.output += child_node.fail.output
                
                queue.append(child_node)

    def search(self, text):
        node = self.root
        result = []

        for i in range(len(text)):
            char = text[i]
            
            # Пропускаем по fail-ссылкам, пока не найдем переход или не дойдем до root
            while node is not self.root and char not in node.children:
                node = node.fail
            
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root
            
            # Добавляем все найденные шаблоны
            for pattern_index in node.output:
                # Позиция конца шаблона (i+1 - длина шаблона + длина шаблона)
                # Но лучше хранить длину шаблона или передавать ее, но в текущей реализации
                # мы не знаем длину шаблона, поэтому просто i+1
                result.append((i + 1 - len(patterns[pattern_index-1]) + 1, pattern_index))
        
        return result

text = input().strip()  # текст
n = int(input().strip())  # количество шаблонов
patterns = [input().strip() for _ in range(n)]  # шаблоны

# Создаем объект алгоритма Ахо-Корасика
ak = AchoKarasik()

# Добавляем шаблоны
for i, pattern in enumerate(patterns):
    ak.add_pattern(pattern, i + 1)

# Строим суффиксные ссылки
ak.build_faillink()

# Запускаем поиск
matches = ak.search(text)

# Сортируем результаты (сначала по позиции, потом по номеру шаблона)
matches.sort()

# Выводим результаты
for pos, pat_num in matches:
    print(pos, pat_num)
