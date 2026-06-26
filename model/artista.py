from dataclasses import dataclass

@dataclass
class Artista:
    ArtistId: int
    Name: str


    def __str__(self):
        return f"{self.Name}"

    def __eq__(self, other):
        if isinstance(other, Artista):
            return self.ArtistId == other.ArtistId
        return False

    def __hash__(self):
        return hash(self.ArtistId)