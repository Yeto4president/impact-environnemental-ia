import { Component, OnInit, inject } from '@angular/core';
import { HeaderComponent } from './components/header/header.component';
import { ConfigPanelComponent } from './components/config-panel/config-panel.component';
import { BestChoiceComponent } from './components/best-choice/best-choice.component';
import { DataService } from './services/data.service';
import { UserConfig, ModeleScore, Modele } from './models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HeaderComponent, ConfigPanelComponent, BestChoiceComponent],
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

  get bestModele(): Modele | null {
    return this.ranked[0]?.modele ?? null;
  }

  get bestScore(): number {
    return this.ranked[0]?.score ?? 0;
  }

  ngOnInit() {
    this.data.getModeles().subscribe(modeles => {
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
