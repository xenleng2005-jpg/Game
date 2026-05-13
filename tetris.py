import pygame
import random
import sys

# --- Constants ---
COLS, ROWS = 10, 20
CELL = 32
SIDEBAR = 200
WIDTH = COLS * CELL + SIDEBAR
HEIGHT = ROWS * CELL
FPS = 60

BLACK  = (0,   0,   0)
GRAY   = (40,  40,  40)
WHITE  = (255, 255, 255)
BORDER = (80,  80,  80)

COLORS = [
    (0,   0,   0),    # empty
    (0,   240, 240),  # I
    (240, 240, 0),    # O
    (160, 0,   240),  # T
    (0,   240, 0),    # S
    (240, 0,   0),    # Z
    (0,   0,   240),  # J
    (240, 160, 0),    # L
]

# Tetrominoes: each piece has 4 rotations, each rotation is a list of (row, col) offsets
PIECES = {
    'I': [
        [(0,0),(0,1),(0,2),(0,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,1),(1,1),(2,1),(3,1)],
    ],
    'O': [
        [(0,0),(0,1),(1,0),(1,1)],
    ] * 4,
    'T': [
        [(0,1),(1,0),(1,1),(1,2)],
        [(0,1),(1,1),(1,2),(2,1)],
        [(1,0),(1,1),(1,2),(2,1)],
        [(0,1),(1,0),(1,1),(2,1)],
    ],
    'S': [
        [(0,1),(0,2),(1,0),(1,1)],
        [(0,1),(1,1),(1,2),(2,2)],
        [(1,1),(1,2),(2,0),(2,1)],
        [(0,0),(1,0),(1,1),(2,1)],
    ],
    'Z': [
        [(0,0),(0,1),(1,1),(1,2)],
        [(0,2),(1,1),(1,2),(2,1)],
        [(1,0),(1,1),(2,1),(2,2)],
        [(0,1),(1,0),(1,1),(2,0)],
    ],
    'J': [
        [(0,0),(1,0),(1,1),(1,2)],
        [(0,1),(0,2),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,0),(2,1)],
    ],
    'L': [
        [(0,2),(1,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(1,2),(2,0)],
        [(0,0),(0,1),(1,1),(2,1)],
    ],
}
PIECE_NAMES = list(PIECES.keys())
PIECE_COLOR = {name: i+1 for i, name in enumerate(PIECE_NAMES)}

SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}
LINES_PER_LEVEL = 10
DROP_INTERVAL_BASE = 800   # ms at level 1
DROP_INTERVAL_MIN  = 80    # ms floor


class Board:
    def __init__(self):
        self.grid = [[0] * COLS for _ in range(ROWS)]

    def is_valid(self, cells):
        for r, c in cells:
            if r < 0 or r >= ROWS or c < 0 or c >= COLS:
                return False
            if self.grid[r][c]:
                return False
        return True

    def lock(self, cells, color):
        for r, c in cells:
            self.grid[r][c] = color

    def clear_lines(self):
        cleared = [r for r in range(ROWS) if all(self.grid[r])]
        for r in cleared:
            del self.grid[r]
            self.grid.insert(0, [0] * COLS)
        return len(cleared)

    def draw(self, surface):
        for r in range(ROWS):
            for c in range(COLS):
                color = COLORS[self.grid[r][c]]
                rect = pygame.Rect(c * CELL, r * CELL, CELL - 1, CELL - 1)
                pygame.draw.rect(surface, color if self.grid[r][c] else GRAY, rect)
                if self.grid[r][c]:
                    pygame.draw.rect(surface, WHITE, rect, 1)


class Piece:
    def __init__(self, name, row=0, col=3):
        self.name  = name
        self.color = PIECE_COLOR[name]
        self.rot   = 0
        self.row   = row
        self.col   = col

    def cells(self, row=None, col=None, rot=None):
        r = self.row if row is None else row
        c = self.col if col is None else col
        rt = self.rot if rot is None else rot
        return [(r + dr, c + dc) for dr, dc in PIECES[self.name][rt % 4]]

    def draw(self, surface, ghost_cells=None):
        if ghost_cells:
            for gr, gc in ghost_cells:
                rect = pygame.Rect(gc * CELL, gr * CELL, CELL - 1, CELL - 1)
                pygame.draw.rect(surface, BORDER, rect, 2)
        for pr, pc in self.cells():
            if pr >= 0:
                rect = pygame.Rect(pc * CELL, pr * CELL, CELL - 1, CELL - 1)
                pygame.draw.rect(surface, COLORS[self.color], rect)
                pygame.draw.rect(surface, WHITE, rect, 1)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock   = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 18)
        self.reset()

    def reset(self):
        self.board      = Board()
        self.score      = 0
        self.lines      = 0
        self.level      = 1
        self.bag        = []
        self.current    = self.new_piece()
        self.next       = self.new_piece()
        self.drop_timer = 0
        self.game_over  = False
        self.paused     = False

    def new_piece(self):
        if not self.bag:
            self.bag = PIECE_NAMES[:]
            random.shuffle(self.bag)
        return Piece(self.bag.pop())

    def drop_interval(self):
        interval = DROP_INTERVAL_BASE - (self.level - 1) * 70
        return max(interval, DROP_INTERVAL_MIN)

    def ghost(self):
        row = self.current.row
        while self.board.is_valid(self.current.cells(row=row + 1)):
            row += 1
        return self.current.cells(row=row)

    def try_move(self, dr=0, dc=0, rot=None):
        r = self.current.row + dr
        c = self.current.col + dc
        new_rot = (self.current.rot + (rot or 0)) % 4
        cells = self.current.cells(row=r, col=c, rot=new_rot)
        if self.board.is_valid(cells):
            self.current.row = r
            self.current.col = c
            self.current.rot = new_rot
            return True
        return False

    def lock_piece(self):
        self.board.lock(self.current.cells(), self.current.color)
        cleared = self.board.clear_lines()
        if cleared:
            self.score += SCORE_TABLE.get(cleared, 0) * self.level
            self.lines += cleared
            self.level = self.lines // LINES_PER_LEVEL + 1
        self.current = self.next
        self.next    = self.new_piece()
        if not self.board.is_valid(self.current.cells()):
            self.game_over = True

    def hard_drop(self):
        while self.try_move(dr=1):
            pass
        self.lock_piece()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    continue
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if self.paused:
                    continue
                if event.key == pygame.K_LEFT:
                    self.try_move(dc=-1)
                elif event.key == pygame.K_RIGHT:
                    self.try_move(dc=1)
                elif event.key == pygame.K_DOWN:
                    self.try_move(dr=1)
                elif event.key == pygame.K_UP:
                    self.try_move(rot=1)
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key == pygame.K_z:
                    self.try_move(rot=-1)

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.drop_timer += dt
        if self.drop_timer >= self.drop_interval():
            self.drop_timer = 0
            if not self.try_move(dr=1):
                self.lock_piece()

    def draw_sidebar(self):
        x = COLS * CELL + 10
        # Next piece preview
        self.screen.blit(self.font_sm.render("NEXT", True, WHITE), (x, 10))
        preview_surf = pygame.Surface((4 * CELL, 4 * CELL))
        preview_surf.fill(BLACK)
        for dr, dc in PIECES[self.next.name][0]:
            r = pygame.Rect(dc * CELL, dr * CELL, CELL - 1, CELL - 1)
            pygame.draw.rect(preview_surf, COLORS[self.next.color], r)
            pygame.draw.rect(preview_surf, WHITE, r, 1)
        self.screen.blit(preview_surf, (x, 36))

        # Stats
        stats = [
            ("SCORE", str(self.score)),
            ("LINES", str(self.lines)),
            ("LEVEL", str(self.level)),
        ]
        y = 36 + 4 * CELL + 20
        for label, value in stats:
            self.screen.blit(self.font_sm.render(label, True, BORDER), (x, y))
            self.screen.blit(self.font_lg.render(value, True, WHITE), (x, y + 20))
            y += 70

        # Controls hint
        hints = ["← → Move", "↑ Rotate R", "Z  Rotate L",
                 "↓ Soft drop", "SPC Hard drop", "P  Pause"]
        y = HEIGHT - len(hints) * 22 - 10
        for h in hints:
            self.screen.blit(self.font_sm.render(h, True, BORDER), (x, y))
            y += 22

    def draw_overlay(self, text, sub=""):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        msg = self.font_lg.render(text, True, WHITE)
        self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        if sub:
            s = self.font_sm.render(sub, True, BORDER)
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    def draw(self):
        self.screen.fill(BLACK)
        # Board grid lines
        for c in range(COLS + 1):
            pygame.draw.line(self.screen, BORDER, (c * CELL, 0), (c * CELL, HEIGHT))
        for r in range(ROWS + 1):
            pygame.draw.line(self.screen, BORDER, (0, r * CELL), (COLS * CELL, r * CELL))

        self.board.draw(self.screen)
        if not self.game_over:
            ghost = self.ghost()
            self.current.draw(self.screen, ghost_cells=ghost)
        self.draw_sidebar()

        if self.game_over:
            self.draw_overlay("GAME OVER", "Press R to restart")
        elif self.paused:
            self.draw_overlay("PAUSED", "Press P to continue")

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
