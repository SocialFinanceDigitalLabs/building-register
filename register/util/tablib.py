from pathlib import Path


def output_tablib(ds, output=None):
    output = output.strip()
    if output is None or output == "" or output == "-":
        print(ds.export('cli'))
    else:
        output = Path(output)
        ext = output.suffix.lower()

        if ext == '.csv':
            with open(output, 'wt') as f:
                f.write(ds.export('csv'))
        elif ext == '.xlsx':
            with open(output, 'wb') as f:
                f.write(ds.export('xlsx'))
