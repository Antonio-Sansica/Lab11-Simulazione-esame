from database.DB_connect import DBConnect
from model.artista import Artista
from model.genere import Genere


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_tutti_i_generi():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None: return result
        try:
            # dictionary=True è OBBLIGATORIO per usare row['NOME_COLONNA']
            cursor = cnx.cursor(dictionary=True)

            # DISTINCT evita doppioni. ORDER BY è utile se devi mostrare i dati in una tendina
            query = """
                SELECT g.*
                FROM Genre g 
                ORDER BY g.Name ASC
                """
            cursor.execute(query)

            for row in cursor:
                genere = Genere(
                    GenreId=row['GenreId'],
                    Name=row['Name'],
                )
                result.append(genere)

            return result
        except Exception as e:
            print(f"Errore DAO estrazione base: {e}")
            return []
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def get_nodi(genereId):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None: return []
        try:
            cursor = cnx.cursor(dictionary=True)

            query = """
                    SELECT DISTINCT a.ArtistId, a.Name
FROM Artist a
JOIN Album al ON a.ArtistId = al.ArtistId
JOIN Track t ON al.AlbumId = t.AlbumId
WHERE t.GenreId = %s
                    """
            cursor.execute(query, (genereId,))

            for row in cursor:
                artista = Artista(
                    ArtistId=row['ArtistId'],
                    Name=row['Name']
                )

                result.append(artista)
            return result

        except Exception as e:
            print(f"Errore DAO ID Nodi Grafo: {e}")
            return []
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def get_archi_non_pesati(genere_id):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None: return []
        try:
            cursor = cnx.cursor(dictionary=True)
            # REGOLA D'ORO: Filtriamo le sotto-query per il genere selezionato (%s)
            # in modo che il cliente comune sia valido solo se ha comprato brani di quel genere!
            query = """
                        SELECT DISTINCT t1.idA AS id1, t2.idA AS id2 
                        FROM
                            (SELECT DISTINCT a.ArtistId AS idA, i.CustomerId AS idC
                             FROM Invoice i
                             JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId 
                             JOIN Track t ON il.TrackId = t.TrackId 
                             JOIN Album a ON t.AlbumId = a.AlbumId
                             WHERE t.GenreId = %s) t1
                        JOIN
                            (SELECT DISTINCT a.ArtistId AS idA, i.CustomerId AS idC
                             FROM Invoice i
                             JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId 
                             JOIN Track t ON il.TrackId = t.TrackId 
                             JOIN Album a ON t.AlbumId = a.AlbumId
                             WHERE t.GenreId = %s) t2
                        ON t1.idC = t2.idC
                        WHERE t1.idA < t2.idA
                        """
            # Passiamo due volte lo stesso genere_id per le due sotto-query
            cursor.execute(query, (genere_id, genere_id))
            for row in cursor:
                result.append((row['id1'], row['id2']))
            return result
        except Exception as e:
            print(f"Errore DAO estrazione archi: {e}")
            return []
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def get_mappa_popolarita(genere_id):
        cnx = DBConnect.get_connection()
        result = {}
        if cnx is None: return result
        try:
            cursor = cnx.cursor(dictionary=True)
            # FONDAMENTALE: JOIN con Invoice (richiesto dalla traccia)
            # e filtro GenreId per non contare brani di altri generi!
            query = """
                        SELECT a.ArtistId AS idA, SUM(il.Quantity) AS popolarita
                        FROM Invoice i
                        JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId 
                        JOIN Track t ON il.TrackId = t.TrackId 
                        JOIN Album a ON t.AlbumId = a.AlbumId
                        WHERE t.GenreId = %s
                        GROUP BY a.ArtistId
                        """
            cursor.execute(query, (genere_id,))
            for row in cursor:
                result[row['idA']] = int(row['popolarita'])
            return result
        except Exception as e:
            print(f"Errore DAO popolarita: {e}")
            return {}
        finally:
            cursor.close()
            cnx.close()