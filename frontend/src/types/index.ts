export interface User {
    id: number
    username: string
    role: 'admin' | 'user'
    avatar?: string
    last_login?: string
    created_at: string
}

export interface Stats {
    total_docs: number
    public_docs: number
    private_docs: number
    total_users: number
}

export interface Document {
    id: number
    title: string
    content: string
    is_public: boolean
    sub_category_id: number
    sort_order: number
    author_id: number
    created_at: string
    updated_at: string
    category_name?: string
    sub_category_name?: string
}

export interface SubCategory {
    id: number
    category_id: number
    name: string
    sort_order: number
    documents: Document[]
}

export interface Category {
    id: number
    name: string
    sort_order: number
    sub_categories: SubCategory[]
}

export interface LoginResponse {
    access_token: string
    token_type: string
}
