import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDGenre(self):
        self._view._ddGenre.options.clear()
        for genere in self._model.get_generi():
            self._view._ddGenre.options.append(ft.dropdown.Option(key=str(genere.GenreId), text=genere.Name))

    def handleCreaGrafo(self, e):
        valore_str = self._view._ddGenre.value
        if valore_str is None:
            self._view.create_alert("Attenzione: seleziona un genere!")

        # 2. CHIAMATA AL MODEL
        self._model.build_graph(valore_str)

        # 3. PULIZIA SCHERMO E VERIFICA
        self._view.txt_result.controls.clear()

        if self._model.grafo.number_of_nodes() == 0:
            self._view.txt_result.controls.append(ft.Text("Nessun grafo creato con questi parametri."))
            self._view.update_page()
            return

        # 4. STAMPA DELLE RISPOSTE STANDARD
        nodi, archi = self._model.get_dettagli_grafo()
        self._view.txt_result.controls.append(ft.Text(f"Grafo creato con successo!", color="green"))
        self._view.txt_result.controls.append(ft.Text(f"Numero Nodi: {nodi}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero Archi: {archi}"))


        self._view.txt_result.controls.append(ft.Text("Archi di peso maggiore:", color="red"))
        top_archi = self._model.get_top_archi_peso(5)
        for u, v, dati in top_archi:
            self._view.txt_result.controls.append(ft.Text(f"{u.Name} -> {v.Name} ({dati['weight']})"))


        #d) ESEMPIO NODO PIÙ INFLUENTE (Solo per grafi Orientati / DiGraph)
        #=== Scommenta per stampare il nodo con bilancio Max (Uscenti - Entranti) ===
        nodo_influente, score_influenza = self._model.get_nodo_piu_influente()
        if nodo_influente is not None:
            self._view.txt_result.controls.append(
                ft.Text(f"Nodo più influente: {nodo_influente.Name} (Score: {score_influenza})", color="blue")
             )

        self._view.update_page()


    def handleCammino(self,e):
        pass