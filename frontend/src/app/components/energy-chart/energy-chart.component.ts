import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { Modele } from '../../models';

interface BarItem {
  nom: string;
  fournisseur: string;
  wh: number;
  co2: number;
  pct: number;
  isBest: boolean;
}

const CONTEXT = 5; // modèles avant et après le choix

@Component({
  selector: 'app-energy-chart',
  standalone: true,
  imports: [CommonModule, DecimalPipe],
  templateUrl: './energy-chart.component.html',
  styleUrl: './energy-chart.component.css'
})
export class EnergyChartComponent implements OnChanges {
  @Input() modeles: Modele[] = [];
  @Input() bestNom: string = '';

  allBars: BarItem[] = [];
  showAll = false;

  get bars(): BarItem[] {
    if (this.showAll) return this.allBars;
    const idx = this.allBars.findIndex(b => b.isBest);
    if (idx === -1) return this.allBars.slice(0, CONTEXT * 2 + 1);
    const start = Math.max(0, idx - CONTEXT);
    const end = Math.min(this.allBars.length, idx + CONTEXT + 1);
    return this.allBars.slice(start, end);
  }

  get bestRank(): number {
    return this.allBars.findIndex(b => b.isBest) + 1;
  }

  ngOnChanges() {
    if (!this.modeles.length) return;

    const sorted = [...this.modeles].sort((a, b) => a.nrg_kwh_moyen - b.nrg_kwh_moyen);
    const maxWh = Math.max(...sorted.map(m => m.nrg_kwh_moyen * 1000));

    this.allBars = sorted.map(m => ({
      nom: m.mdl_nom,
      fournisseur: m.frs_nom,
      wh: m.nrg_kwh_moyen * 1000,
      co2: m.frs_co2_datacenter,
      pct: (m.nrg_kwh_moyen * 1000 / maxWh) * 100,
      isBest: m.mdl_nom === this.bestNom,
    }));

    // Réinitialise la vue réduite quand le modèle change
    this.showAll = false;
  }
}
