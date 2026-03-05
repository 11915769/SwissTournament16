import { Injectable } from '@angular/core';
import { timer, combineLatest } from 'rxjs';
import { switchMap, shareReplay, startWith } from 'rxjs/operators';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class LiveTournamentService {
  private tick$ = timer(0, 300000000000000);

  state$ = this.tick$.pipe(
    switchMap(() => this.api.tournamentState()),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  standings$ = this.tick$.pipe(
    switchMap(() => this.api.standings()),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  bracket$ = this.tick$.pipe(
    switchMap(() => this.api.bracket()),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  summary$ = combineLatest([
    this.state$.pipe(startWith(null)),
    this.standings$.pipe(startWith(null)),
    this.bracket$.pipe(startWith(null)),
  ]).pipe(
    shareReplay({ bufferSize: 1, refCount: true })
  );

  constructor(private api: ApiService) {}
}
