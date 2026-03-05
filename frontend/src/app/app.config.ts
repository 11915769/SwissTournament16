import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi, HTTP_INTERCEPTORS } from '@angular/common/http';
import { routes } from './app.routes';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { getAuth, provideAuth } from '@angular/fire/auth';
import { getFirestore, provideFirestore } from '@angular/fire/firestore';
import {AuthInterceptor} from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [provideZoneChangeDetection({ eventCoalescing: true }), provideHttpClient(withInterceptorsFromDi()),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }, provideRouter(routes), provideFirebaseApp(() => initializeApp({ projectId: "kniffelswiss16", appId: "1:325815791854:web:cfd1da855001b2a47883ff", storageBucket: "kniffelswiss16.firebasestorage.app", apiKey: "AIzaSyCNPyJy1KGWSOSxoTxYffwpe1HV2bjeJjc", authDomain: "kniffelswiss16.firebaseapp.com", messagingSenderId: "325815791854", measurementId: "G-NWCXTQWKT1"})), provideAuth(() => getAuth()), provideFirestore(() => getFirestore())]
};
