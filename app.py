import PySimpleGUI as sg
from collections import deque
from queue import PriorityQueue

# Rozmiar naszego okna
WIDTH = 1230    # +30 px, bo z jakiegoś powodu PySimple ma dziwne paddingi i ucina ostatnią kolumnę rysowanego grafu na canvie
HEIGHT = 800
CELL_SIZE = 40
rows = 20
cols = 30
grid = [[0 for _ in range(rows)] for _ in range(cols)]  # fill zerami

queue = deque()             # kolejka kolejno odwiedzonych wierzchołków w BFS
stack = []                  # stos kolejno odwiedzonych wierzchołków w DFS
open_list = PriorityQueue() # kolejka priorytetowa dla A* do wyboru węzła o najniższym koszcie
closed_list = set()         # zbiór dla A* mówiący, czy w tym wierzchołku byliśmy
visited = set()             # zbiór odwiedzonych wierzchołków
parent = {}                 # wymagane do odtworzenia ścieżki

g_score = {}    # koszt od startu do wierzchołka
h_score = {}    # heurystyka: koszt od wierzchołka do celu
f_score = {}    # f = g + h (łączny koszt, wg którego wybieramy najlepszy węzeł - wybieramy jak najmniejszą wartość)

bfs_running = False
dfs_running = False
a_star_running = False

start, end = None, None
found = False

colors = {
    0: "#aaaaaa",  # puste
    1: "black",    # ściana
    2: "green",    # start
    3: "red",      # cel
    4: "yellow",   # odwiedzony
    5: "blue"      # sciezka
}

directions = [
    (0, 1),  # góra
    (1, 0),  # prawo
    (0, -1), # dół
    (-1, 0)  # lewo
]

def draw_grid(color):
    graph = window["graph"]
    for x in range(cols):
        for y in range(rows):
            x0 = x * CELL_SIZE
            y0 = y * CELL_SIZE
            graph.draw_rectangle(
                (x0, y0),
                (x0 + CELL_SIZE, y0 + CELL_SIZE),
                fill_color=color,
                line_color="#1100ff",
            )

# funkcja do kolorowania pojedyńczej celi (x,y ) określonym kolorem
def paint_cell(x, y, color):
    graph = window["graph"]

    x0 = x * CELL_SIZE
    y0 = y * CELL_SIZE

    graph.draw_rectangle(
        (x0, y0),
        (x0 + CELL_SIZE, y0 + CELL_SIZE),
        fill_color=color,
        line_color="#1100ff"
    )

def reset():
    global queue, stack, visited, parent, bfs_running, dfs_running, a_star_running, found, start, end, grid

    queue = deque()
    stack = []
    visited = set()
    parent = {}

    bfs_running = False
    dfs_running = False
    a_star_running = False
    found = False
    start = None
    end = None

    grid = [[0 for _ in range(rows)] for _ in range(cols)]

    draw_grid(colors[0])


def reconstruct_path():
    node = end  # rekonstruujemy od końca

    while node != start:
        x, y = node # tupla (x, y)

        if node != start and node != end:
            paint_cell(x, y, colors[5])

        node = parent[node] # previous

def bfs_init():
    global queue, visited, parent, bfs_running, found

    #inicjalizacja / reset
    queue = deque()
    visited = set()
    parent = {}

    queue.append(start)
    visited.add(start)

    bfs_running = True
    found = False

def bfs_step():
    global queue, visited, parent, found

    if found:   # ściezka odnaleziona
        return False

    if len(queue) == 0: # pusta kolejka (done)
        return False

    x, y = queue.popleft()  # wzięcie elementu z początku kolejki

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < cols and 0 <= ny < rows:
            if grid[nx][ny] != 1 and (nx, ny) not in visited: # nie jest odwiedzony i nie jest ścianą

                if (nx, ny) == end:  # odnaleziono ścieżkę start -> end
                    print("Odnaleziono sciezke")
                    parent[(nx, ny)] = (x, y)
                    found = True
                    reconstruct_path()
                    return False

                visited.add((nx, ny))       # odwiedzamy
                parent[(nx, ny)] = (x, y)   # parent = element z początku kolejki
                queue.append((nx, ny))      # dodajemy do kolejki nowo odryty element

                paint_cell(nx, ny, colors[4])   # paint
    return True

def bfs(solve):
    global bfs_running

    if start is None or end is None:
        return

    if not bfs_running:
        bfs_init()

    if solve:   # gdy przycisk solve
        while bfs_step() is True:
            continue
    else:       # gdy przycisk step
        bfs_step()


def dfs_init():
    global stack, visited, parent, dfs_running, found

    # inicjalizacja / reset
    stack = []
    visited = set()
    parent = {}

    stack.append(start)
    visited.add(start)

    dfs_running = True
    found = False

def dfs_step():
    global stack, visited, parent, found

    if found:  # ściezka odnaleziona
        return False

    if len(stack) == 0:  # pusty stos(done)
        return False

    x, y = stack.pop()  # wzięcie elementu z KOŃCA KOLEJKI (stosu) w odróżnieniu od BFS

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < cols and 0 <= ny < rows:
            if grid[nx][ny] != 1 and (nx, ny) not in visited:  # nie jest odwiedzony i nie jest ścianą

                if (nx, ny) == end:  # odnaleziono ścieżkę start -> end
                    print("Odnaleziono sciezke")
                    parent[(nx, ny)] = (x, y)
                    found = True
                    reconstruct_path()
                    return False

                visited.add((nx, ny))  # odwiedzamy
                parent[(nx, ny)] = (x, y)  # parent = element z początku stosu
                stack.append((nx, ny))  # dodajemy do stosu nowo odryty element

                paint_cell(nx, ny, colors[4])  # paint
    return True

def dfs(solve):
    global dfs_running

    if start is None or end is None:
        return

    if not dfs_running:
        dfs_init()

    if solve:   # gdy przycisk solve
        while dfs_step() is True:
            continue
    else:       # gdy przycisk step
        dfs_step()


def manhattan(a, b):     # dla ruchu w 4 kierunkach (góra/dół/lewo/prawo)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def diagonal(a, b):     # dla ruchu w 8 kierunkach
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy)

def euclidean(a, b):     # dla dowolnego kierunku
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2) ** 0.5

def a_star_init():
    global open_list, closed_list, visited, parent
    global a_star_running, found, g_score, h_score, f_score

    if start is None or end is None:
        return

    # inicjalizacja / reset
    open_list = PriorityQueue()
    closed_list = set()
    visited = set()
    parent = {}

    g_score = {}
    h_score = {}
    f_score = {}

    g_score[start] = 0
    h_score[start] = manhattan(start, end)
    f_score[start] = g_score[start] + h_score[start]

    open_list.put((f_score[start], start))

    a_star_running = True
    found = False

def a_star_step():
    global open_list, closed_list, parent, found
    global g_score, h_score, f_score

    if found:
        return False

    if open_list.empty():
        return False

    f, current = open_list.get()    # f_score niepotrzebny, ale Prioryty Queue porównuje pierwszy element tupli,
                                    #  dlatego ogólnie tam jest. Na przykład: (5, (1,1)) < (10, (3,5))
    if current in closed_list:
        return True

    if current == end:
        print("Odnaleziono sciezke")
        found = True
        reconstruct_path()
        return False

    closed_list.add(current)

    x, y = current  # rozpakowanie tupli

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        neighbor = (nx, ny)

        if not (0 <= nx < cols and 0 <= ny < rows): # zabezpieczenie boundaries
            continue

        if grid[nx][ny] == 1:   # ściana
            continue

        if neighbor in closed_list: # już wcześniej odwiedzony
            continue

        tmp_g = g_score[current] + 1

        if neighbor not in g_score or tmp_g < g_score[neighbor]:
            parent[neighbor] = current

            g_score[neighbor] = tmp_g
            h_score[neighbor] = manhattan(neighbor, end)
            f_score[neighbor] = g_score[neighbor] + h_score[neighbor]

            open_list.put((f_score[neighbor], neighbor))

            if neighbor != start and neighbor != end:
                paint_cell(nx, ny, colors[4])   # odwiedzony

    return True

def a_star(solve):
    global a_star_running

    if start is None or end is None:
        return

    if not a_star_running:
        a_star_init()

    if solve:   # gdy przycisk solve
        while a_star_step() is True:
            continue
    else:       # gdy przycisk step
        a_star_step()


# układ elementów w oknie, przyjmuje listę list. Co ciekawe, minimalnie musi istnieć co najmniej jeden wiersz.
# Przykładowe elementy dla layout to:
# text() - zwykły wyświetlany tekst
# Combo() - lista rozwijana
# Spin() - wybór liczby z określonego zakresu
# Button() - przycisk
# Checkbox() - checkbox()
# Graph() - obszar do rysowania
layout = [
    #[sg.Text("asd"), sg.Spin([1,2,3,4,5], 1, 1)],
    [sg.Graph(
        canvas_size=(WIDTH, HEIGHT-40), # -40 by zrobić miejsce na przyciski, rysunek na canvie zostanie odpowiednio przeskalowany
        graph_bottom_left=(0, 0),
        graph_top_right=(WIDTH, HEIGHT),
        background_color="#333333",  # Wytłumaczyć RGB
        key="graph",
        enable_events=True, # umożliwienie eventow klikania myszką na canvie
        drag_submits=True   # umożliwienie eventow "dragowania" myszką na canvie
    )],
    [sg.Button("Next step"),
     sg.Button("Solve"),
     sg.Button("Reset"),
     # Wybór algorytmu values["algorithm"] zwraca aktualnie wybraną opcję (BFS/DFS/A*)
     # readonly zapobiega ręcznemu wpisywaniu nieistniejącego algorytmu
     # emable_events umożliwia odczyt aktualnie wybranej wartości
     sg.Combo(["BFS", "DFS", "A*"], default_value="BFS", key="algorithm", readonly=True, enable_events=True)],
]


window = sg.Window("Window", layout, size=(WIDTH, HEIGHT), background_color="#444444", finalize=True)

# łączenie wydarzeń kliknięcia LPM i PPM na grafie
window["graph"].bind("<B1-Motion>", "LMB")   # bind_string: " <Button-1> " dla pojedyńczych kliknięć, " <B1-Motion> " dla dragowania
window["graph"].bind("<Button-2>", "MMB")   # scroll click
window["graph"].bind("<B3-Motion>", "RMB")

draw_grid(colors[0])

# główna pętla nasłuchująca wydarzenia
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    # Obsługa przycisków

    algo = values["algorithm"]

    if event == "algorithm" or event == "Reset":
        reset()
        continue

    if event == "Solve":
        if algo == "BFS":
            bfs(solve=True)
        elif algo == "DFS":
            dfs(solve=True)
        elif algo == "A*":
            a_star(solve=True)

    if event == "Next step":
        if algo == "BFS":
            bfs(solve=False)
        elif algo == "DFS":
            dfs(solve=False)
        elif algo == "A*":
            a_star(solve=False)


    # Obsługa myszki

    x, y = values["graph"]

    if x is None or y is None:
        continue


    gx = int(x // CELL_SIZE)
    gy = int(y // CELL_SIZE)

    if not (0 <= gx < cols and 0 <= gy < rows): # zabezpieczenie przed wyjściem po za zakres grafu
        continue

    # ustawienie/usunięcie blokady na klikniętej celi:

    if event in ("graphLMB", "graphRMB"):
        if grid[gx][gy] in (2, 3):  # start / end
            continue

        if event == "graphLMB":
            grid[gx][gy] = 1
            paint_cell(gx, gy, colors[1])   # ściana

        elif event == "graphRMB":
            grid[gx][gy] = 0
            paint_cell(gx, gy, colors[0])   # puste


    # ustawienie startu/końca/wymazanie ich
    if event == "graphMMB":
        if start is None:
            start = (gx, gy)
            grid[gx][gy] = 2
            paint_cell(gx, gy, colors[2])

        elif end is None:
            end = (gx, gy)
            grid[gx][gy] = 3
            paint_cell(gx, gy, colors[3])

        else:
            s0 = start[0]   # s0, s1 = start
            s1 = start[1]
            e0 = end[0]
            e1 = end[1]

            grid[s0][s1] = 0
            grid[e0][e1] = 0

            paint_cell(s0, s1, colors[0])
            paint_cell(e0, e1, colors[0])

            start = end = None

    algo = values["algorithm"]

window.close()




