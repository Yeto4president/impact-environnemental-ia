import { Component, OnInit, inject } from '@angular/core';
import { forkJoin } from 'rxjs';
import { HeaderComponent } from './components/header/header.component';
import { ConfigPanelComponent } from './components/config-panel/config-panel.component';
import { BestChoiceComponent } from './components/best-choice/best-choice.component';
import { ImpactTranslatorComponent } from './components/impact-translator/impact-translator.component';
import { EnergyChartComponent } from './components/energy-chart/energy-chart.component';
import { DataService } from './services/data.service';
import { UserConfig, ModeleScore, Modele, EquivalenceModele } from './models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HeaderComponent, ConfigPanelComponent, BestChoiceComponent, ImpactTranslatorComponent, EnergyChartComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private data = inject(DataService);

  config: UserConfig = {
    tache: 'toutes',
    poidsEco: 60,
    poidsPerf: 60,
    poidsPrix: 40,
    poidsTransparence: 30,
  };

  ranked: ModeleScore[] = [];
  modeles: Modele[] = [];
  equivalences: EquivalenceModele[] = [];
  maxCo2 = 0;

  get bestModele(): Modele | null { return this.ranked[0]?.modele ?? null; }
  get bestScore(): number { return this.ranked[0]?.score ?? 0; }
  get bestEquiv(): EquivalenceModele | null {
    if (!this.bestModele) return null;
    return this.equivalences.find(e => e.mdl_nom === this.bestModele!.mdl_nom) ?? null;
  }

  ngOnInit() {
    forkJoin({
      modeles: this.data.getModeles(),
      equivData: this.data.getEquivalences(),
    }).subscribe(({ modeles, equivData }) => {
      this.modeles = modeles;
      this.equivalences = equivData.modeles;
      this.maxCo2 = Math.max(...equivData.modeles.map(e => e.co2_g_par_requete));
      this.ranked = this.data.rankModeles(modeles, this.config);
    });
  }

  onConfigChange(config: UserConfig) {
    this.config = config;
    this.data.getModeles().subscribe(modeles => {
      this.ranked = this.data.rankModeles(modeles, this.config);
    });
  }
}
