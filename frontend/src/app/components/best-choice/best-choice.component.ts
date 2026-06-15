import { Component, Input } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { Modele } from '../../models';

@Component({
  selector: 'app-best-choice',
  standalone: true,
  imports: [CommonModule, DecimalPipe],
  templateUrl: './best-choice.component.html',
  styleUrl: './best-choice.component.css'
})
export class BestChoiceComponent {
  @Input() modele: Modele | null = null;
  @Input() score: number = 0;

  get scoreBarres() {
    if (!this.modele) return [];
    return [
      { label: 'Écologique',   hint: 'Comparé aux 112 modèles : plus c\'est haut, moins il consomme',                          value: this.modele.score_eco,          color: '#22c55e' },
      { label: 'Performance',  hint: 'Part des utilisateurs ayant préféré ce modèle lors de tests en aveugle',                  value: this.modele.score_perf,         color: '#3b82f6' },
      { label: 'Prix',         hint: 'Comparé aux 112 modèles : plus c\'est haut, moins il coûte cher à utiliser',              value: this.modele.score_prix,         color: '#f59e0b' },
      { label: 'Transparence', hint: 'Score FMTI : mesure si l\'entreprise communique ouvertement sur son modèle (0 = opaque)', value: this.modele.score_transparence, color: '#a78bfa' },
    ];
  }

  // Tarif réglementé EDF 2025 (option Base TTC)
  private readonly TARIF_KWH = 0.2516;

  get coutElec1000requetes(): number {
    if (!this.modele) return 0;
    return this.modele.nrg_kwh_moyen * 1000 * this.TARIF_KWH;
  }

  get co2ParPays(): string {
    if (!this.modele) return '—';
    return this.modele.frs_co2_datacenter.toFixed(3) + ' kg CO₂/kWh';
  }
}
