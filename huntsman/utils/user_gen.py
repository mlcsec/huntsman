import itertools

def generate_usernames(first_names, last_names, file=None):
    combinations = []
    
    for first, last in itertools.product(first_names, last_names):
        first_initial = first[0]
        last_initial = last[0]
        first_three = first[:3]
        last_three = last[:3]

        combinations.extend([
            f"{first}.{last}",
            f"{first}_{last}",
            f"{first}{last}",
            f"{first}{last_initial}",
            f"{first}_{last_initial}",
            f"{first}.{last_initial}",
            f"{first_initial}.{last}",
            f"{first_initial}_{last}",
            f"{first_initial}{last}",
            f"{first_three}{last_three}",
            f"{last}.{first}",
            f"{last}_{first}",
            f"{last}{first}",
            f"{last}{first_initial}",
            f"{last}_{first_initial}",
            f"{last}.{first_initial}",
            f"{last_initial}.{first}",
            f"{last_initial}_{first}",
            f"{last_initial}{first}",
            f"{last_three}{first_three}"
        ])
    
    return combinations