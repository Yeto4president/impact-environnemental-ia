import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UserConfig, TacheId } from '../../models';

export const TACHES: { id: TacheId; label: string; description: string }[] = [
  { id: 'toutes',          label: 'Toutes les tâches',  description: 'Compare les modèles sur l\'ensemble de leurs usages' },
  { id: 'gpqa',            label: 'Questions complexes', description: 'Poser des questions pointues en science, médecine ou droit' },
  { id: 'image-chat',      label: 'Analyser une image',  description: 'Décrire, comprendre ou extraire des infos d\'une photo' },
  { id: 'lm-arena-chat',  label: 'Conversation',        description: 'Discuter, rédiger ou obtenir des explications claires' },
  { id: 'sourcegraph-fim', label: 'Écrire du code',      description: 'Générer, compléter ou corriger du code informatique' },
];

@Component({
  selector: 'app-config-panel',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './config-panel.component.html',
  styleUrl: './config-panel.component.css'
})
export class ConfigPanelComponent implements OnInit {
  @Output() configChange = new EventEmitter<UserConfig>();

  taches = TACHES;

  config: UserConfig = {
    tache: 'toutes',
    poidsEco: 60,
    poidsPerf: 60,
    poidsPrix: 40,
    poidsTransparence: 30,
  };

  sliders = [
    { key: 'poidsEco',          label: 'Écologique',   color: '#22c55e', info: 'Montez si la consommation d\'énergie et le CO₂ émis comptent pour vous.' },
    { key: 'poidsPerf',         label: 'Performance',  color: '#3b82f6', info: 'Montez si vous voulez les réponses les plus précises et pertinentes.' },
    { key: 'poidsPrix',         label: 'Prix',         color: '#f59e0b', info: 'Montez si vous voulez privilégier les modèles les moins chers à utiliser.' },
    { key: 'poidsTransparence', label: 'Transparence', color: '#a78bfa', info: 'Montez si vous voulez favoriser les entreprises qui communiquent ouvertement.' },
  ];

  ngOnInit() { this.emit(); }

  getValue(key: string): number { return (this.config as any)[key]; }

  setValue(key: string, value: number) {
    (this.config as any)[key] = +value;
    this.emit();
  }

  emit() { this.configChange.emit({ ...this.config }); }
}
