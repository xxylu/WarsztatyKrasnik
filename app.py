import PySimpleGUI as sg
from collections import deque

# Rozmiar naszego okna
WIDTH = 1230    # +30 px, bo z jakiegoś powodu PySimple ma dziwne paddingi i ucina ostatnią kolumnę rysowanego grafu na canvie
HEIGHT = 800
CELL_SIZE = 40
rows = 20
cols = 30
grid = [[0 for _ in range(rows)] for _ in range(cols)]  # fill zerami

queue = deque()         # kolejka kolejno odwiedzonych wierzchołków w BFS
visited = set()         # zbiór odwiedzonych wierzchołków
parent = {}             # wymagane do odtworzenia ścieżki
bfs_running = False

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
    global queue, visited, parent, bfs_running, found, start, end, grid

    queue = deque()
    visited = set()
    parent = {}

    bfs_running = False
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

    if solve:
        while bfs_step() is True:
            continue
    else:
        bfs_step()




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

    x, y = values["graph"]


    gx = int(x // CELL_SIZE)
    gy = int(y // CELL_SIZE)

    if not (0 <= gx < cols and 0 <= gy < rows): # zabezpieczenie przed wyjściem po za zakres grafu
        continue

    # ustawienie/usunięcie blokady na klikniętej celi:
    if event in ("graphLMB", "graphRMB"):
        if event == "graphLMB":
            if grid[gx][gy] == 2 or grid[gx][gy] == 3:  # continue dla początku / końca
                continue
            grid[gx][gy] = 1
            paint_cell(gx, gy, colors[1])

        elif event == "graphRMB":
            if grid[gx][gy] == 2 or grid[gx][gy] == 3:  # continue dla początku / końca
                continue
            grid[gx][gy] = 0
            paint_cell(gx, gy, colors[0])


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
            s0 = start[0]
            s1 = start[1]
            e0 = end[0]
            e1 = end[1]

            grid[s0][s1] = grid[e0][e1] = 0
            paint_cell(s0, s1, colors[0])
            paint_cell(e0, e1, colors[0])
            start = end = None

    if event == "Solve":
        bfs(solve=True)

    if event == "Next step":
        bfs(solve=False)

    if event == "Reset":
        reset()

window.close()




