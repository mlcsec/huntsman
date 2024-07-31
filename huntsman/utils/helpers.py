from colorama import init, Fore, Style

def print_section_header(title: str, file=None):
    header = f"\n{'=' * 50}\n{title:^50}\n{'=' * 50}"
    print(f"{Fore.CYAN}{Style.BRIGHT}{header}{Style.RESET_ALL}")
    if file:
        file.write(f"{header}\n")

def print_info(label: str, value: str, color: str, file=None):
    print(f"{color}{label}:{Style.RESET_ALL} {value}")
    if file:
        file.write(f"{label}: {value}\n")