// Portfolio Service - Firestore operations for saving/loading portfolio analyses
import {
    collection,
    addDoc,
    getDocs,
    updateDoc,
    deleteDoc,
    doc,
    query,
    orderBy,
    serverTimestamp
} from 'firebase/firestore'
import { db } from '../firebase'

// Save a new portfolio analysis
export async function saveAnalysis(userId, analysisData) {
    const userAnalysesRef = collection(db, 'users', userId, 'analyses')

    const docData = {
        ...analysisData,
        savedAt: serverTimestamp(),
        name: analysisData.name || `Portfolio Analysis - ${new Date().toLocaleDateString()}`
    }

    const docRef = await addDoc(userAnalysesRef, docData)
    return docRef.id
}

// Get all analyses for a user
export async function getUserAnalyses(userId) {
    const userAnalysesRef = collection(db, 'users', userId, 'analyses')
    const q = query(userAnalysesRef, orderBy('savedAt', 'desc'))

    const snapshot = await getDocs(q)
    const analyses = []

    snapshot.forEach((doc) => {
        analyses.push({
            id: doc.id,
            ...doc.data()
        })
    })

    return analyses
}

// Update an analysis (e.g., rename)
export async function updateAnalysis(userId, analysisId, data) {
    const docRef = doc(db, 'users', userId, 'analyses', analysisId)
    await updateDoc(docRef, {
        ...data,
        updatedAt: serverTimestamp()
    })
}

// Delete an analysis
export async function deleteAnalysis(userId, analysisId) {
    const docRef = doc(db, 'users', userId, 'analyses', analysisId)
    await deleteDoc(docRef)
}
