import json
import re
import sys
import os

class LayParserError(Exception):
    """Error específico para archivos .lay"""
    pass

def parse_lay_line(line: str):
    line = line.strip()
    if not line:
        return None

    match_command = re.match(r'^\[(\w+)\]\s*[:=]\s*(.+)$', line)
    if match_command:
        name, command = match_command.groups()
        return f"#{name}", command.strip()


    match_function = re.match(r'^\{(\w+)\}\s*[:=]\s*<(.+)>$', line)
    if match_function:
        name, content = match_function.groups()
        commands = []

        parts = re.split(r',(?![^"]*"\s*,)', content)

        for part in parts:
            part = part.strip()
            if part.startswith('"') and part.endswith('"'):
                commands.append(part.strip('"'))
            elif part.startswith("wait(") and part.endswith(")"):
                try:
                    value = int(part[5:-1])
                    commands.append(value)
                except ValueError:
                    raise LayParserError(f"Error en wait(): {part}")
            else:
                raise LayParserError(f"Estructura inválida en función: {part}")

        return f"!{name}", commands

    raise LayParserError(f"Línea inválida: {line}")

def parse_lay_file(filename: str):
    result = {}
    with open(filename, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            try:
                parsed = parse_lay_line(line)
                if parsed:
                    key, value = parsed
                    result[key] = value
            except LayParserError as e:
                raise LayParserError(f"Error en línea {i}: {e}")
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python lay.py archivo.lay")
        sys.exit(1)

    filename = sys.argv[1]

    if not filename.endswith(".layclt"):
        print("❌ El archivo debe tener extensión .lay")
        sys.exit(1)

    try:
        data = parse_lay_file(filename)

        out_file = os.path.splitext(filename)[0] + ".json"

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✅ Archivo convertido correctamente → {out_file}")

    except LayParserError as e:
        print(f"❌ Error: {e}")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {filename}")
