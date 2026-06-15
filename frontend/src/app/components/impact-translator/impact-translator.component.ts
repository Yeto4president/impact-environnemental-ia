import { Component, Input } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { EquivalenceModele } from '../../models';

@Component({
  selector: 'app-impact-translator',
  standalone: true,
  imports: [CommonModule, DecimalPipe],
  templateUrl: './impact-translator.component.html',
  styleUrl: './impact-translator.component.css'
})
export class ImpactTranslatorComponent {
  @Input() equiv: EquivalenceModele | null = null;
  @Input() maxCo2: number = 10;

  readonly SCALE = 1000;

  // Seuils absolus basés sur la distribution réelle des 112 modèles
  // Moyenne : 2.24g | max outlier : 78g (grok-4.20)
  private readonly SEUIL_BAS = 0.5;   // g CO₂
  private readonly SEUIL_MID = 3.0;   // g CO₂
  private readonly ECHELLE_MAX = 10;  // g CO₂ — cap visuel

  get co2Pct(): number {
    if (!this.equiv) return 0;
    return Math.min(100, (this.equiv.co2_g_par_requete / this.ECHELLE_MAX) * 100);
  }

  get co2Level(): 'low' | 'mid' | 'high' {
    if (!this.equiv) return 'low';
    const co2 = this.equiv.co2_g_par_requete;
    if (co2 < this.SEUIL_BAS) return 'low';
    if (co2 < this.SEUIL_MID) return 'mid';
    return 'high';
  }

  get co2Label(): string {
    if (this.co2Level === 'low') return 'Faible impact (< 0.5 g CO₂)';
    if (this.co2Level === 'mid') return 'Impact modéré (0.5 – 3 g CO₂)';
    return 'Impact élevé (> 3 g CO₂)';
  }

  get equivalences() {
    if (!this.equiv) return [];
    const e = this.equiv.equivalences;
    const s = this.SCALE;

    const ledMin = e.min_led_9w * s;
    const batPct = e.pct_batterie_smartphone * s;
    const streamMin = e.min_streaming_hd * s;

    return [
      {
        value: ledMin >= 60
          ? `${(ledMin / 60).toFixed(1)} h`
          : `${ledMin.toFixed(0)} min`,
        label: 'une ampoule LED allumée'
      },
      {
        value: batPct >= 100
          ? `${(batPct / 100).toFixed(1)} charges`
          : `${batPct.toFixed(0)} %`,
        label: batPct >= 100 ? 'charges d\'iPhone 15 complètes (15 Wh)' : 'de la batterie d\'un iPhone 15 (15 Wh)'
      },
      {
        value: streamMin >= 60
          ? `${(streamMin / 60).toFixed(1)} h`
          : `${streamMin.toFixed(0)} min`,
        label: 'de streaming vidéo HD'
      },
    ];
  }
}
