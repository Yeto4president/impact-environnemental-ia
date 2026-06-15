import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import {
  Modele, EquivalencesData, Fournisseur,
  BenchmarkTache, DetecteurGaspillage, UserConfig, ModeleScore
} from '../models';

@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);

  private modeles$ = this.http.get<Modele[]>('modeles_normalises.json').pipe(shareReplay(1));
  private equivalences$ = this.http.get<EquivalencesData>('equivalences.json').pipe(shareReplay(1));
  private fournisseurs$ = this.http.get<Fournisseur[]>('fournisseurs.json').pipe(shareReplay(1));
  private benchmark$ = this.http.get<BenchmarkTache[]>('benchmark_taches.json').pipe(shareReplay(1));
  private gaspillage$ = this.http.get<DetecteurGaspillage[]>('detecteur_gaspillage.json').pipe(shareReplay(1));

  getModeles(): Observable<Modele[]> { return this.modeles$; }
  getEquivalences(): Observable<EquivalencesData> { return this.equivalences$; }
  getFournisseurs(): Observable<Fournisseur[]> { return this.fournisseurs$; }
  getBenchmark(): Observable<BenchmarkTache[]> { return this.benchmark$; }
  getDetecteurGaspillage(): Observable<DetecteurGaspillage[]> { return this.gaspillage$; }

  computeScore(modele: Modele, config: UserConfig): number {
    const total = config.poidsEco + config.poidsPerf + config.poidsPrix + config.poidsTransparence;
    if (total === 0) return 0;
    return (
      (modele.score_eco          ?? 0) * (config.poidsEco          / total) +
      (modele.score_perf         ?? 0) * (config.poidsPerf         / total) +
      (modele.score_prix         ?? 0) * (config.poidsPrix         / total) +
      (modele.score_transparence ?? 0) * (config.poidsTransparence / total)
    ) * 100;
  }

  rankModeles(modeles: Modele[], config: UserConfig): ModeleScore[] {
    return modeles
      .map(m => ({ modele: m, score: this.computeScore(m, config) }))
      .sort((a, b) => b.score - a.score);
  }
}
