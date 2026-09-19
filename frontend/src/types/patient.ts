export interface Patient {
  id: number
  hospital_id: number
  mrn: string
  medical_record_number?: string
  first_name: string
  last_name: string
  date_of_birth?: string | null
  gender?: string | null
  phone?: string | null
  phone_number?: string | null
  email?: string | null
  communication_consent: boolean
  preferred_language?: string | null
  preferred_call_time?: string | null
  is_active: boolean
  created_at?: string
  updated_at?: string
}
