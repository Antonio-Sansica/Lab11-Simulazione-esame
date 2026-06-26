from dataclasses import dataclass

@dataclass
class Genere:
    GenreId: int
    Name: str


    def __str__(self):
        return f"{self.Name}"

    def __eq__(self, other):
        if isinstance(other, Genere):
            return self.GenreId == other.GenreId
        return False

    def __hash__(self):
        return hash(self.GenreId)