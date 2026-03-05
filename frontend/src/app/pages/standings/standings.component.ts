import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LiveTournamentService } from '../../services/live-tournament.service';

@Component({
  selector: 'app-standings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './standings.component.html',
})
export class StandingsComponent {
  readonly standings$;
  readonly state$;

  constructor(live: LiveTournamentService) {
    this.standings$ = live.standings$;
    this.state$ = live.state$;
  }
}
