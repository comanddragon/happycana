import os
import re
import subprocess

def get_pkgs(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.read().splitlines()
        return [
            re.split(r'==|>|<|\[', l.strip())[0].lower().replace('-', '_')
            for l in lines if l.strip() and not l.startswith(('#', '-r'))
        ]
    except Exception:
        return []

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_txt = os.path.join(script_dir, 'base.txt')
    prod_txt = os.path.join(script_dir, 'production.txt')
    output_txt = os.path.join(script_dir, 'requirements.txt')  # Saved directly next to the script
    prod_pkgs = set(get_pkgs(base_txt) + get_pkgs(prod_txt))
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True, check=True)
    frozen_lines = result.stdout.splitlines()

    with open(output_txt, 'w') as f:
        for line in frozen_lines:
            pkg = re.split(r'==|>|<|\[', line.strip())[0].lower().replace('-', '_')
            if pkg in prod_pkgs:
                f.write(line + '\n')

if __name__ == "__main__":
    main()