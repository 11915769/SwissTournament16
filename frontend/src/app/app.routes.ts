import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { AppShellComponent } from './layout/app-shell/app-shell.component';
import { StandingsComponent } from './pages/standings/standings.component';
import { BracketComponent } from './pages/bracket/bracket.component';
import { RulesComponent } from './pages/rules/rules.component';
import { AdminComponent } from './pages/admin/admin.component';
import { JoinComponent } from './pages/join/join.component';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';
import {registeredGuard} from './guards/registered.guard';
import { MatchesComponent } from './pages/matches/matches.component';



export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: AppShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'join' },

      { path: 'join', component: JoinComponent },

      { path: 'standings', component: StandingsComponent, canActivate: [registeredGuard] },
      { path: 'bracket', component: BracketComponent, canActivate: [registeredGuard] },
      { path: 'rules', component: RulesComponent, canActivate: [registeredGuard] },
      { path: 'matches', component: MatchesComponent, canActivate: [registeredGuard] },
      { path: 'admin', component: AdminComponent, canActivate: [adminGuard] },
    ],
  },

  { path: '**', redirectTo: '' },
];
