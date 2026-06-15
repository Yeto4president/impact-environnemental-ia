export interface Modele {
  mdl_nom: string;
  frs_nom: string;
  frs_pays_datacenter: string;
  frs_co2_datacenter: number;
  frs_score_fmti: number;
  nrg_nb_conversations: number;
  nrg_kwh_moyen: number;
  nrg_wh_par_token: number;
  qlt_taux_satisfaction: number;
  qlt_taux_victoire: number;
  trf_input_1k: number;
  trf_output_1k: number;
  score_eco: number;
  score_perf: number;
  score_prix: number;
  score_transparence: number;
  score_efficience: number;
}

export interface EquivalenceModele {
  mdl_nom: string;
  frs_nom: string | null;
  pays_datacenter: string | null;
  kwh_par_requete: number;
  co2_g_par_requete: number;
  wh_par_token: number;
  nb_conversations: number;
  equivalences: {
    min_led_9w: number;
    km_voiture_electrique: number;
    pct_batterie_smartphone: number;
    min_streaming_hd: number;
    equiv_recherches_google: number;
  };
}

export interface EquivalencesData {
  meta: {
    nb_modeles: number;
    kwh_moyen_global: number;
    co2_moyen_global_g: number;
  };
  modeles: EquivalenceModele[];
}

export interface Fournisseur {
  frs_nom: string;
  frs_pays_datacenter: string;
  frs_co2_datacenter: number;
  frs_score_fmti: number;
  score_upstream: number;
  score_model: number;
  score_downstream: number;
  kwh_moyen_fournisseur: number | null;
}

export interface BenchmarkTache {
  mdl_nom: string;
  frs_nom: string;
  btk_tache: string;
  btk_gpu_modele: string;
  btk_nb_gpu: number;
  btk_joules_par_token: number;
  btk_kwh_par_1k_tokens: number;
  btk_watt_moyen: number;
  btk_debit_tokens_s: number;
  btk_latence_itl_ms: number;
}

export interface DetecteurGaspillage {
  mdl_nom: string;
  frs_nom: string;
  nrg_wh_par_token: number;
  nrg_kwh_moyen: number;
  ratio_reel_sur_labo: number;
  score_frugalite: number;
}

export interface UserConfig {
  profil: string;
  casUsage: string;
  poidsEco: number;
  poidsPerf: number;
  poidsPrix: number;
}

export interface ModeleScore {
  modele: Modele;
  score: number;
}
