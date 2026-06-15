import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeleScore } from '../../models';

type SortKey = 'score' | 'score_eco' | 'score_perf' | 'score_prix' | 'score_transparence' | 'nrg_kwh_moyen';

@Component({
  selector: 'app-ranking-table',
  standalone: true,
  imports: [CommonModule, DecimalPipe, FormsModule],
  templateUrl: './ranking-table.component.html',
  styleUrl: './ranking-table.component.css'
})
export class RankingTableComponent {
  @Input() ranked: ModeleScore[] = [];
  @Input() selectedNom: string = '';
  @Output() selectModele = new EventEmitter<ModeleScore>();

  search = '';
  filterFournisseur = '';
  sortKey: SortKey = 'score';
  sortDir: 'desc' | 'asc' = 'desc';

  get fournisseurs(): string[] {
    return [...new Set(this.ranked.map(r => r.modele.frs_nom).filter(Boolean))].sort();
  }

  get filtered(): ModeleScore[] {
    let list = [...this.ranked];

    if (this.search.trim()) {
      const q = this.search.toLowerCase();
      list = list.filter(r =>
        r.modele.mdl_nom.toLowerCase().includes(q) ||
        r.modele.frs_nom?.toLowerCase().includes(q)
      );
    }

    if (this.filterFournisseur) {
      list = list.filter(r => r.modele.frs_nom === this.filterFournisseur);
    }

    list.sort((a, b) => {
      const va = this.sortKey === 'score' ? a.score / 100 : (a.modele as any)[this.sortKey];
      const vb = this.sortKey === 'score' ? b.score / 100 : (b.modele as any)[this.sortKey];
      return this.sortDir === 'desc' ? vb - va : va - vb;
    });

    return list;
  }

  sort(key: SortKey) {
    if (this.sortKey === key) {
      this.sortDir = this.sortDir === 'desc' ? 'asc' : 'desc';
    } else {
      this.sortKey = key;
      this.sortDir = 'desc';
    }
  }

  sortIcon(key: SortKey): string {
    if (this.sortKey !== key) return '↕';
    return this.sortDir === 'desc' ? '↓' : '↑';
  }

  rankOf(item: ModeleScore): number {
    return this.ranked.indexOf(item) + 1;
  }

  medal(rank: number): string {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return String(rank);
  }
}
