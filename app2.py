from _pyrepl.commands import end

import PySimpleGUI as sg
from collections import deque

# Rozmiar naszego okna
WIDTH = 1230    # +30 px bo z jakiegos powodu dziwne paddingi ucinaja ostatnia kolumne grafu na canvie
HEIGHT = 800

CELL_SIZE = 40
rows = 20
cols = 30
grid = [[0 for _ in range(rows)] for _ in range(cols)] # fill zerami

start, end = None, None

queue = deque()             # kolejka kolejno odwiedzonych wierzcholkow w bfs
stack = []                  # stos kolejno odwiedzonych wierzcholkow w bfs
visited = set()             # zbior odwiedzonych wierzcholkow
parent = {}                 # wymagane do odtworzenia sciezki

bfs_running = False
dfs_running = False
found = False

colors = {
    0: "#aaaaaa",   # puste
    1: "black",     # sciana
    2: "green",     # start
    3: "red",       # cel
    4: "yellow",    # odwiedzony
    5: "blue"       # sciezka
}

directions = [
    (0, 1),     # gora
    (1, 0),     # prawo
    (0, -1),    # dol
    (-1, 0),    # lewo
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

# funkcja do kolorowania pojedynczej celi (x, y) okreslonym kolorem
def paint_cell(x, y, color):
    graph = window["graph"]

    x0 = x * CELL_SIZE
    y0 = y * CELL_SIZE

    graph.draw_rectangle(
        (x0, y0),
        (x0 + CELL_SIZE, y0 + CELL_SIZE),
        fill_color=color,
        line_color="#1100ff",
    )

def reset():
    global queue, stack, visited, parent, bfs_running, dfs_running, found, start, end, grid

    queue = deque()
    stack = []
    visited = set()
    parent = {}
    start = None
    end = None

    bfs_running = False
    dfs_running = False
    found = False

    draw_grid(colors[0])

def reconstruct_path():
    node = end # rekonstruujemy od końca

    while node != start:
        x, y = node # tuple

        if node != start and node != end:
            paint_cell(x, y, colors[5]) # niebieski

        node = parent[node]


def bfs_init():
    global queue, visited, parent, bfs_running, found

    queue = deque()
    visited = set()
    parent = {}

    queue.append(start)
    visited.add(start)

    bfs_running = True
    found = False

def bfs_step():
    global queue, visited, parent, found

    if found: #sciezka odnaleziona
        return False

    if len(queue) == 0: # pusta kolejka (done)
        return False

    x, y = queue.popleft()  # wziecie elementu z poczatku kolejki

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < cols and 0 <= ny < rows:
            if grid[nx][ny] != 1 and (nx, ny) not in visited: # nie jest odwiedzony i nie jest sciana

                if (nx, ny) == end:  # odnaleziono sciezke start -> end
                    print("Odnaleziono sciezke")
                    parent[(nx, ny)] = (x, y)
                    found = True
                    reconstruct_path()
                    return False

                visited.add((nx, ny))       # odwiedzamy
                parent[(nx, ny)] = (x, y)   # parent = element z poczatku kolejki
                queue.append((nx, ny))      # dodajemy do kolejki nowo odkryty element

                paint_cell(nx, ny, colors[4])   # paint
    return True


def bfs(solve):
    global bfs_running

    if start is None or end is None:
        return

    if not bfs_running:
        bfs_init()

    if solve:           # gdy przycisk solve
        while bfs_step() is True:
            continue
    else:
        bfs_step()      # gdy przycisk step


def dfs_init():
    global stack, visited, parent, dfs_running, found

    stack = []
    visited = set()
    parent = {}

    stack.append(start)
    visited.add(start)

    dfs_running = True
    found = False

def dfs_step():
    global stack, visited, parent, found

    if found: #sciezka odnaleziona
        return False

    if len(stack) == 0: # pusta kolejka (done)
        return False

    x, y = stack.pop()  # wziecie elementu z konca kolejki

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < cols and 0 <= ny < rows:
            if grid[nx][ny] != 1 and (nx, ny) not in visited: # nie jest odwiedzony i nie jest sciana
                if (nx, ny) == end:  # odnaleziono sciezke start -> end
                    print("Odnaleziono sciezke")
                    parent[(nx, ny)] = (x, y)
                    found = True
                    reconstruct_path()
                    return False

                visited.add((nx, ny))       # odwiedzamy
                parent[(nx, ny)] = (x, y)   # parent = element z poczatku kolejki
                stack.append((nx, ny))      # dodajemy do kolejki nowo odkryty element

                paint_cell(nx, ny, colors[4])   # paint
    return True


def dfs(solve):
    global dfs_running

    if start is None or end is None:
        return

    if not dfs_running:
        dfs_init()

    if solve:           # gdy przycisk solve
        while dfs_step() is True:
            continue
    else:
        dfs_step()      # gdy przycisk step



# uklad elementow w oknie przyjmuje liste list. co ciekawe, minimalnei musi istniec co najmniej jeden wiersz.
# przykladowe elemnty dla layout to:
# text() - zwykly wyswietlany tekst
# combo() - lista rozwijana
# spin() - wybor liczby zo kreslonego zakresu
# button() - przycisk
# checkbox() - checkbox()
# graph() - obszar do rysowania
layout = [
    [sg.Graph(
        canvas_size=(WIDTH, HEIGHT-40),
        graph_bottom_left=(0, 0),
        graph_top_right=(WIDTH, HEIGHT),
        background_color='#333333',
        key="graph",
        enable_events=True,
        drag_submits=True
    )],
    [sg.Button("Next step"),
     sg.Button("Solve"),
     sg.Button("Reset"),
     sg.Combo(["BFS", "DFS"], default_value="BFS", key="algorithm", readonly=True, enable_events=True),]
]

window = sg.Window("Window", layout, size=(WIDTH, HEIGHT), background_color='#444444', finalize = True)

# laczenie wydarzen klikniecia LPM i PPM na grafie. Button dla pojedynczego klikniecia, motion dla dragowania
window["graph"].bind("<B1-Motion>", "LMB")      # LPM
window["graph"].bind("<Button-2>", "MMB")       # scroll click
window["graph"].bind("<B3-Motion>", "RMB")      # RPM

draw_grid(colors[0])

# glowna petla nasluchujaca wydarzenia
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    # obsluga przyciskow

    algo = values["algorithm"]

    if event == "algorithm" or event == "Reset":
        reset()
        continue

    if event == "Solve":
        if algo == "BFS":
            bfs(solve=True)
        elif algo == "DFS":
            dfs(solve=True)

    if event == "Next step":
        if algo == "BFS":
            bfs(solve=False)
        elif algo == "DFS":
            dfs(solve=False)

    # obsluga myszki

    x, y = values["graph"]

    if x is None or y is None:
        continue

    gx = int(x // CELL_SIZE)
    gy = int(y // CELL_SIZE)

    if not (0 <= gx < cols and 0 <= gy < rows):     # zabezpieczenie przed wyjsciem po za zakres grafu myszka
        continue

    # ustawienie/usuniecie blokady na kliknietej celi:

    if event in ("graphLMB", "graphRMB"):
        if grid[gx][gy] in (2, 3):  # start, end
            continue

        if event == "graphLMB":
            grid[gx][gy] = 1
            paint_cell(gx, gy, colors[1])   # sciana

        elif event == "graphRMB":
            grid[gx][gy] = 0
            paint_cell(gx, gy, colors[0])   # puste

    # ustawienie startu/konca/wymazanie ich
    if event == "graphMMB":
        if start is None:
            start = (gx, gy)
            grid[gx][gy] = 2    # zielony
            paint_cell(gx, gy, colors[2])

        elif end is None:
            end = (gx, gy)
            grid[gx][gy] = 3    # czerwony
            paint_cell(gx, gy, colors[3])

        else:
            s0 = start[0]   # s0, s1 = start
            s1 = start[1]
            e0 = end[0]
            e1 = end[1]

            grid[s0][s1] = 0
            grid[e0][e1] = 1

            paint_cell(s0, s1, colors[0])
            paint_cell(e0, e1, colors[0])

            start = end = None

window.close()