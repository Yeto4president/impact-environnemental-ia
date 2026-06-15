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

  get co2Pct(): number {
    if (!this.equiv) return 0;
    return Math.min(100, (this.equiv.co2_g_par_requete / this.maxCo2) * 100);
  }

  get co2Level(): 'low' | 'mid' | 'high' {
    if (this.co2Pct < 25) return 'low';
    if (this.co2Pct < 65) return 'mid';
    return 'high';
  }

  get co2Label(): string {
    if (this.co2Level === 'low') return 'Très faible impact';
    if (this.co2Level === 'mid') return 'Impact modéré';
    return 'Impact élevé';
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
