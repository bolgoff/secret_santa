import random

def match_players(players_ids: list[int], exclusions: list[tuple[int, int]]) -> dict[int, int] | None:
    givers = players_ids[:]
    receivers = players_ids[:]
    
    for _ in range(10000):
        random.shuffle(receivers)
        is_valid = True
        matches = {}
        
        for giver, receiver in zip(givers, receivers):
            if giver == receiver:
                is_valid = False
                break
            if (giver, receiver) in exclusions:
                is_valid = False
                break
            matches[giver] = receiver
            
        if is_valid:
            return matches
    return None