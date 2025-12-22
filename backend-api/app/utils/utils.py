from .logger import Logger
movies = [{'id': 1, 'name': 'spiderman3', 'rate': 3.9},
          {'id': 2, 'name': 'taken 3', 'rate': 2.4}]

users = []


L = Logger('logs.txt')

def get_achievement_points(rarity: str) -> int:
    """Get points for achievement based on rarity - shared utility function"""
    rarity_points = {
        'common': 10,
        'rare': 20,
        'epic': 40,
        'legendary': 80
    }
    return rarity_points.get(rarity, 10)  # default to common if rarity not found