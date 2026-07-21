with col_bd2:
        st.markdown("### 📂 Integrazione File CSV")
        st.info(
            "Carica un file CSV. L'ordine atteso per colonna è: Alimento, gr/n, carbo, proteine, grassi, kcal."
        )
        file_caricato = st.file_uploader(
            "Carica file CSV", type=["csv"], key="uploader_banca_dati"
        )

        if file_caricato is not None:
            try:
                df_nuovo = None
                try:
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=None, engine="python"
                    )
                except UnicodeDecodeError:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato,
                        encoding="latin-1",
                        sep=None,
                        engine="python",
                    )
                except Exception:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=";", engine="python"
                    )

                if df_nuovo is not None and not df_nuovo.empty:
                    st.write("Anteprima dati letti dal file:", df_nuovo.head())
                    if st.button("Conferma e Aggiungi alla Banca Dati"):
                        colonne_attese = [
                            "Alimento",
                            "gr/n",
                            "carbo",
                            "proteine",
                            "grassi",
                            "kcal",
                        ]

                        # Pulizia e standardizzazione nomi colonne
                        cols_orig = [str(c).strip().lower() for c in df_nuovo.columns]
                        df_nuovo.columns = cols_orig

                        mapping_colonne = {}
                        for c in cols_orig:
                            if "alimento" in c or "nome" in c:
                                mapping_colonne[c] = "Alimento"
                            elif "gr" in c or "quant" in c or "peso" in c or "numero" in c:
                                mapping_colonne[c] = "gr/n"
                            elif "carb" in c:
                                mapping_colonne[c] = "carbo"
                            elif "prot" in c:
                                mapping_colonne[c] = "proteine"
                            elif "grass" in c or "fat" in c:
                                mapping_colonne[c] = "grassi"
                            elif "kcal" in c or "calorie" in c:
                                mapping_colonne[c] = "kcal"

                        df_nuovo = df_nuovo.rename(columns=mapping_colonne)
                        # Elimina eventuali colonne duplicate dopo il mapping
                        df_nuovo = df_nuovo.loc[:, ~df_nuovo.columns.duplicated()]

                        presenti = [
                            col for col in colonne_attese if col in df_nuovo.columns
                        ]
                        if len(presenti) < 4 and len(df_nuovo.columns) >= 4:
                            col_mapping_pos = {}
                            for idx, col_name in enumerate(df_nuovo.columns):
                                if idx < len(colonne_attese):
                                    col_mapping_pos[col_name] = colonne_attese[idx]
                            df_nuovo = df_nuovo.rename(columns=col_mapping_pos)
                            df_nuovo = df_nuovo.loc[:, ~df_nuovo.columns.duplicated()]

                        # Costruzione sicura del DataFrame tramite dizionario
                        data_dict = {}
                        for col in colonne_attese:
                            if col in df_nuovo.columns:
                                data_dict[col] = df_nuovo[col].values
                            else:
                                data_dict[col] = (
                                    0 if col != "Alimento" else "Sconosciuto"
                                )

                        df_finale = pd.DataFrame(data_dict)

                        # Pulizia righe vuote o non valide
                        df_finale = df_finale.dropna(subset=["Alimento"])
                        df_finale = df_finale[
                            df_finale["Alimento"].astype(str).str.strip() != ""
                        ]

                        # Aggiornamento dello stato e salvataggio su disco
                        st.session_state.banca_dati_df = (
                            pd.concat(
                                [st.session_state.banca_dati_df, df_finale],
                                ignore_index=True,
                            )
                            .drop_duplicates(subset=["Alimento"])
                            .reset_index(drop=True)
                        )
                        salva_dati_disco()
                        st.success(
                            "Banca dati aggiornata con successo dal file CSV!"
                        )
                        st.rerun()
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")
