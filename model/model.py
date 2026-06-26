from database.DAO import DAO
import networkx as nx


class Model:
    def __init__(self):
        self.mappa_generi = {}
        self.popola_mappa_generi()
        self.grafo = nx.DiGraph()


    def get_generi(self):
        return DAO.get_tutti_i_generi()

    def popola_mappa_generi(self):
        lista_generi = DAO.get_tutti_i_generi()
        for genere in lista_generi:
            self.mappa_generi[genere.GenreId] = genere


    def get_oggetto_da_cache(self, id_cercato):
        return self.mappa_generi.get(int(id_cercato), None)

    def build_graph(self, parametro_utente):
        self.grafo.clear()
        mappa_nodi = {}

        # 1. Carico i Nodi del genere selezionato
        for nodo in DAO.get_nodi(parametro_utente):
            mappa_nodi[int(nodo.ArtistId)] = nodo
        self.grafo.add_nodes_from(mappa_nodi.values())

        # 2. Carico la mappa delle popolarità (Usa la variante globale o di genere)
        cache_popolarita = DAO.get_mappa_popolarita(parametro_utente)

        # 3. Estraggo gli Archi filtrati per il genere dell'esame
        archi_grezzi = DAO.get_archi_non_pesati(parametro_utente)

        for id_1, id_2 in archi_grezzi:
            # Esaminiamo solo le coppie i cui artisti fanno parte dei nostri nodi
            if id_1 in mappa_nodi and id_2 in mappa_nodi:
                n1 = mappa_nodi[id_1]
                n2 = mappa_nodi[id_2]

                # Recuperiamo le popolarità in modo sicuro
                peso1 = cache_popolarita.get(id_1, 0)
                peso2 = cache_popolarita.get(id_2, 0)

                peso_arco = peso1 + peso2

                # Applichiamo i versi in base alla popolarità
                if peso1 > peso2:
                    self.grafo.add_edge(n1, n2, weight=peso_arco)
                elif peso1 < peso2:
                    self.grafo.add_edge(n2, n1, weight=peso_arco)
                else:
                    # Caso parità: inserisco entrambi i versi
                    self.grafo.add_edge(n1, n2, weight=peso_arco)
                    self.grafo.add_edge(n2, n1, weight=peso_arco)
    def get_nodo_piu_influente(self):
        if self.grafo.number_of_nodes() == 0:
            return None, 0

        max_influenza = -float('inf')
        miglior_nodo = None

        for nodo in self.grafo.nodes():
            # CORRETTO: Ora usa 'weight' invece di 'peso'!
            peso_entrante = self.grafo.in_degree(nodo, weight='weight')
            peso_uscente = self.grafo.out_degree(nodo, weight='weight')

            influenza = peso_uscente - peso_entrante

            if influenza > max_influenza:
                max_influenza = influenza
                miglior_nodo = nodo

        return miglior_nodo, max_influenza
    def get_dettagli_grafo(self):
        return self.grafo.number_of_nodes(), self.grafo.number_of_edges()


    def get_top_archi_peso(self, n):
        lista_archi = list(self.grafo.edges(data=True))

        # 2. Li ordino in base al valore 'weight' dentro il dizionario 'data', al contrario (decrescente)
        lista_archi.sort(key=lambda edge: edge[2]['weight'], reverse=True)

        # 3. Restituisco i primi N elementi
        return lista_archi[:n]


