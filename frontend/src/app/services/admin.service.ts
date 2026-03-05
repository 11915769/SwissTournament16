import { Injectable, computed } from '@angular/core';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AdminService {
  isAdmin = computed(() => {
    const email = (this.auth.getEmail() || '').toLowerCase();
    return environment.adminEmails.map(e => e.toLowerCase()).includes(email);
  });

  constructor(private auth: AuthService) {}
}
