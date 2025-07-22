import { supabase } from "../lib/supabaseClient";

export const fetchPublicPuzzles = async () => {
    const { data, error } = await supabase
        .from("puzzles")
        .select("*")
        .eq("is_public", true)
        .order("created_at", {ascending: false})

    if (error) throw error
    return data
}

export const fetchPuzzleById = async (id: string) => {
    const {data, error} = await supabase
        .from("puzzles")
        .select("*")
        .eq("id", id)
        .single()
    
    if (error) throw error
    return data
}

export const createPuzzle = async (puzzleData: {
    title: string
    categories: any[]
    difficulty?: number
}) => {
    const {data, error} = await supabase
        .from("puzzles")
        .insert([{ ...puzzleData, is_public: false}])
        .select()

    if (error) throw error
    return data[0]
}