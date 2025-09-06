# Connor's Lightning Parser Overlays (LPO)

Connor's Lightning Parser Overlays (LPO) is an overlay generation utility for different sensors onto the Lightning Parser Lib (LPL).

> [!NOTE]
> It is an important note that this project does NOT depend on LPL, to avoid circular dependancy.

## Useful Functions (for my own self for maintenance)

- Run in background: `python main.py > output.log 2>&1 & disown`

- List all files in directory './' and sizes: `du -h --max-depth=1 ./ | sort -hr`

> - `python main.py`
>
> - `python main.py > output.log 2>&1 & disown`
>
> - `pip install -r requirements.txt`
>
> - `pip show setuptools`
>
> - `python3 -m build`

## Building from source

**Build:** 

`python -m build`

**Then upload:**

- `python -m twine upload dist/*`

or

- `python -m twine upload --repository lightning_parser_overlays dist/*`