import { createContext, useContext, useEffect, useState } from "react"
import { supabase } from "../lib/supabaseClient"
import type { Session, User } from "@supabase/supabase-js"

type AuthContextType = {
    user: User | null
    session: Session | null
    isGuest: boolean
    signIn: (email: string, password: string) => Promise<void>
    signUp: (email: string, password: string) => Promise<void>
    signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({children}: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null> (null)
    const [session, setSession] = useState<Session | null>(null)
    const [isGuest, setIsGuest] = useState(false)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: {session} }) => {
            setSession(session)
            setUser(session?.user ?? null)
        })

        const { data: authListener } = supabase.auth.onAuthStateChange(
            async (event, session) => {
                setSession(session)
                setUser(session?.user ?? null)
            }
        )

        return () => {
            authListener.subscription.unsubscribe()
        }
    }, [])

    const signIn = async (email: string, password: string) => {
        const {error} = await supabase.auth.signInWithPassword({email, password})
        if (error) throw error
    }

    const signUp = async (email: string, password: string) => {
        const {error} = await supabase.auth.signUp({email, password})
        if (error) throw error
    }

    const signOut = async () => {
        await supabase.auth.signOut()
    }

    return (
        <AuthContext.Provider
            value = {{user, session, isGuest, signIn, signUp, signOut }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)