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

  bars: BarItem[] = [];

  ngOnChanges() {
    if (!this.modeles.length) return;

    const sorted = [...this.modeles].sort((a, b) => a.nrg_kwh_moyen - b.nrg_kwh_moyen);
    const maxWh = Math.max(...sorted.map(m => m.nrg_kwh_moyen * 1000));

    this.bars = sorted.map(m => ({
      nom: m.mdl_nom,
      fournisseur: m.frs_nom,
      wh: m.nrg_kwh_moyen * 1000,
      co2: m.frs_co2_datacenter,
      pct: (m.nrg_kwh_moyen * 1000 / maxWh) * 100,
      isBest: m.mdl_nom === this.bestNom,
    }));
  }
}
