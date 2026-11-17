"""Construye el ZIP instalable desde moodle_plugin/videorec y verifica sus bytes."""
import argparse
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "moodle_plugin/videorec"
MIRROR = ROOT / "videorec"
OUTPUT = ROOT / "block_videorec.zip"


def archivos():
    return {str(p.relative_to(SOURCE)): p.read_bytes() for p in sorted(SOURCE.rglob("*")) if p.is_file()}


def verificar():
    expected = {"videorec/" + path: content for path, content in archivos().items()}
    with ZipFile(OUTPUT) as archive:
        if set(archive.namelist()) != set(expected):
            raise ValueError("El ZIP no coincide con los archivos del plugin")
        for name, content in expected.items():
            if archive.read(name) != content:
                raise ValueError("Archivo desactualizado en ZIP: " + name)
    mirror = {str(p.relative_to(MIRROR)): p.read_bytes() for p in MIRROR.rglob("*") if p.is_file()}
    if mirror != archivos():
        raise ValueError("La copia videorec no coincide con moodle_plugin/videorec")
    print(f"ZIP verificado: {OUTPUT.name}, {len(expected)} archivos, raíz videorec/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        shutil.copytree(SOURCE, MIRROR, dirs_exist_ok=True)
        with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
            for path, content in archivos().items():
                info = ZipInfo("videorec/" + path, date_time=(2026, 11, 17, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                archive.writestr(info, content)
    verificar()


if __name__ == "__main__":
    main()
