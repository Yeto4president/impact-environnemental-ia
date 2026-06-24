import { Component, Input } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { Modele, UserConfig } from '../../models';

type WeightKey = 'poidsEco' | 'poidsPerf' | 'poidsPrix' | 'poidsTransparence';

type ScoreBreakdownItem = {
  label: string;
  hint: string;
  description: string;
  value: number;
  color: string;
  icon: string;
  sliderKey: WeightKey;
};

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
  @Input() totalModeles: number = 0;
  @Input() config: UserConfig | null = null;

  get scoreBarres(): ScoreBreakdownItem[] {
    if (!this.modele) return [];
    return [
      {
        label: 'Écologique',
        hint: 'Part du score écologique dans le comparatif des 112 modèles',
        value: this.modele.score_eco,
        color: '#22c55e',
        icon: '🌳',
        sliderKey: 'poidsEco',
        description: 'mesure l\'impact environnemental du modèle par rapport aux 112 modèles de la base',
      },
      {
        label: 'Performance',
        hint: 'Part du score performance dans le comparatif des 112 modèles',
        value: this.modele.score_perf,
        color: '#3b82f6',
        icon: '⚡',
        sliderKey: 'poidsPerf',
        description: 'compare la qualité de réponse du modèle aux 112 modèles référencés',
      },
      {
        label: 'Prix',
        hint: 'Part du score prix dans le comparatif des 112 modèles',
        value: this.modele.score_prix,
        color: '#f59e0b',
        icon: '💸',
        sliderKey: 'poidsPrix',
        description: 'indique si le modèle est plus économique que les autres modèles de la base',
      },
      {
        label: 'Transparence',
        hint: 'Part du score transparence dans le comparatif des 112 modèles',
        value: this.modele.score_transparence,
        color: '#a78bfa',
        icon: '🔎',
        sliderKey: 'poidsTransparence',
        description: 'mesure la qualité des informations publiques face aux 112 modèles comparés',
      },
    ];
  }

  get scoreBreakdown(): Array<{ label: string; description: string; valueText: string; color: string; icon: string }> {
    if (!this.modele) return [];

    return this.scoreBarres.map(item => ({
      label: item.label,
      description: item.description,
      valueText: `${Math.round(item.value * 100)}%`,
      color: item.color,
      icon: item.icon,
    }));
  }

  get activePriorities(): Array<{ label: string; weight: number; valueText: string; color: string; icon: string }> {
    const config = this.config;
    if (!config) return [];

    return this.scoreBarres
      .map(item => ({
        label: item.label,
        weight: config[item.sliderKey],
        valueText: `${Math.round(item.value * 100)}%`,
        color: item.color,
        icon: item.icon,
      }))
      .filter(item => item.weight > 0)
      .sort((a, b) => b.weight - a.weight);
  }

  get comparisonText(): string {
    const total = this.totalModeles || 112;
    return `Chaque pourcentage ci-dessous correspond au score du modèle dans le comparatif des ${total} modèles disponibles.`;
  }

  get summaryReason(): string {
    if (!this.modele) return '';

    const priorities = this.activePriorities;
    if (!priorities.length) {
      return `Le classement utilise vos réglages actuels, mais aucun critère n'est priorisé.`;
    }

    const strongestWeight = priorities[0]?.weight ?? 0;
    const strongest = priorities.filter(item => item.weight === strongestWeight).slice(0, 2);
    const priorityText = strongest.map(item => `${item.label} (${item.weight}%)`).join(' et ');

    return `Vous avez surtout donné du poids à ${priorityText}. Selon vos priorités, ce modèle est le meilleur choix parmi les ${this.totalModeles || 112} modèles.`;
  }

  get compactFacts(): Array<{ label: string; value: string; color: string }> {
    if (!this.modele) return [];

    return [
      {
        label: 'Conso.',
        value: `${(this.modele.nrg_kwh_moyen * 1000).toFixed(2)} Wh / requête`,
        color: '#22c55e',
      },
      {
        label: 'Satisfaction',
        value: `${Math.round(this.modele.qlt_taux_satisfaction * 100)}%`,
        color: '#3b82f6',
      },
      {
        label: 'Prix',
        value: `${this.modele.trf_input_1k.toFixed(4)} $ / 1k tokens`,
        color: '#f59e0b',
      },
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
