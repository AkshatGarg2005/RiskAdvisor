// Firebase configuration and initialization
import { initializeApp } from "firebase/app"
import { getAuth } from "firebase/auth"
import { getFirestore } from "firebase/firestore"

// Firebase configuration from user
const firebaseConfig = {
    apiKey: "AIzaSyD9vB68jYx5CKXyBU2Si3PukcEyqjcf3i8",
    authDomain: "investmentanalyser-5dc85.firebaseapp.com",
    projectId: "investmentanalyser-5dc85",
    storageBucket: "investmentanalyser-5dc85.firebasestorage.app",
    messagingSenderId: "1085762525014",
    appId: "1:1085762525014:web:f629bef21cec8af0bca8f7",
    measurementId: "G-GR85SF857W"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize services
export const auth = getAuth(app)
export const db = getFirestore(app)

export default app
