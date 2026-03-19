"""Grid/map beheer voor GPA Defenders."""

from src.settings import SCREEN_WIDTH, TILE_SIZE, GRID_COLS, GRID_ROWS


class GridMap:
    """Beheert het speelveld, pad en bouwregels."""

    def __init__(self):
        self.grid: list[list[int]] = []
        self.waypoints: list[tuple[int, int]] = []
        self._setup_grid()

    def _setup_grid(self) -> None:
        """Maak het grid en definieer het vijandpad."""
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        y_row_2 = 2 * TILE_SIZE + TILE_SIZE // 2
        y_row_5 = 5 * TILE_SIZE + TILE_SIZE // 2
        x_col_4 = 4 * TILE_SIZE + TILE_SIZE // 2
        x_col_10 = 10 * TILE_SIZE + TILE_SIZE // 2

        # S-vormig voorbeeldpad
        self.waypoints = [
            (-TILE_SIZE // 2, y_row_2),
            (x_col_4, y_row_2),
            (x_col_4, y_row_5),
            (x_col_10, y_row_5),
            (x_col_10, y_row_2),
            (SCREEN_WIDTH + TILE_SIZE // 2, y_row_2),
        ]

        # Markeer pad-cellen in het grid
        for i in range(len(self.waypoints) - 1):
            x1, y1 = self.waypoints[i]
            x2, y2 = self.waypoints[i + 1]
            gx1, gy1 = int(x1 // TILE_SIZE), int(y1 // TILE_SIZE)
            gx2, gy2 = int(x2 // TILE_SIZE), int(y2 // TILE_SIZE)

            if gy1 == gy2:  # horizontaal
                for gx in range(min(gx1, gx2), max(gx1, gx2) + 1):
                    if 0 <= gx < GRID_COLS and 0 <= gy1 < GRID_ROWS:
                        self.grid[gy1][gx] = 1
            elif gx1 == gx2:  # verticaal
                for gy in range(min(gy1, gy2), max(gy1, gy2) + 1):
                    if 0 <= gx1 < GRID_COLS and 0 <= gy < GRID_ROWS:
                        self.grid[gy][gx1] = 1

    def is_within_bounds(self, grid_x: int, grid_y: int) -> bool:
        """Check of een cel binnen het speelveld valt."""
        return 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS

    def can_place_tower(self, grid_x: int, grid_y: int) -> bool:
        """Check of op deze cel een toren geplaatst mag worden."""
        if not self.is_within_bounds(grid_x, grid_y):
            return False
        return self.grid[grid_y][grid_x] == 0

    def place_tower(self, grid_x: int, grid_y: int) -> bool:
        """Markeer een cel als bezet door een toren."""
        if not self.can_place_tower(grid_x, grid_y):
            return False
        self.grid[grid_y][grid_x] = 2
        return True

    def remove_tower(self, grid_x: int, grid_y: int) -> bool:
        """Maak een torencel weer vrij."""
        if not self.is_within_bounds(grid_x, grid_y):
            return False
        if self.grid[grid_y][grid_x] != 2:
            return False
        self.grid[grid_y][grid_x] = 0
        return True
