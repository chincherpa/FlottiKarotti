from rich.console import Console
import _banners

console = Console()

console.print(f'{_banners.sHole}', style="blink")

console.print([1, 2, 3])
console.print("[blue underline]Looks like a link")
console.print(locals())
console.print("FOO", style="white on blue")
console.print("FOO", style="blink")

from time import sleep

from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.panel import Panel

console = Console()

with console.screen(style="bold white on red") as screen:
    text = Align.center(
        Text.from_markup(f"[blink]Don't Panic![/blink]\nLutz", justify="center"),
        vertical="middle",
    )
    screen.update(Panel(text))
