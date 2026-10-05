#!/bin/sh
# Установка на Linux и macOS: найти подходящий Python и передать ему дело.
# Вся работа — в install.py; здесь только поиск интерпретатора, потому что
# до его запуска спросить больше некого.
set -eu

here=$(cd "$(dirname "$0")" && pwd)

for candidate in python3.13 python3.12 python3.11 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
        exec "$candidate" "$here/install.py" "$@"
    fi
done

echo "Python 3.10 or newer was not found." >&2
echo "Не найден Python 3.10 или новее." >&2
case "$(uname -s)" in
    Darwin) echo "  brew install python      (or https://www.python.org/downloads/)" >&2 ;;
    *) echo "  sudo apt-get install python3 python3-venv      (Debian, Ubuntu)" >&2
       echo "  sudo dnf install python3                       (Fedora)" >&2 ;;
esac
exit 2
