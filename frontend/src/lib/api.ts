export const API_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000"


export type AppointmentAgenda = {
  id: number
  business_id: number
  service_id: number
  service_name: string
  staff_member_id: number
  staff_first_name: string
  staff_last_name: string | null
  customer_name: string
  customer_email: string
  customer_phone: string | null
  start_datetime: string
  end_datetime: string
  status: string
}

export async function getAppointmentsForDate(
  businessId: number,
  targetDate: string,
): Promise<AppointmentAgenda[]> {
  const params = new URLSearchParams({
    target_date: targetDate,
  })

  const response = await fetch(
    `${API_URL}/businesses/${businessId}/appointments?${params}`,
  )

  if (!response.ok) {
    throw new Error(
      `Unable to load appointments (${response.status})`,
    )
  }

  return response.json() as Promise<AppointmentAgenda[]>
}


export type OpeningHour = {
  id: number
  business_id: number
  weekday: number
  start_time: string
  end_time: string
}

export async function getOpeningHours(
  businessId: number,
): Promise<OpeningHour[]> {
  const response = await fetch(
    `${API_URL}/businesses/${businessId}/opening-hours`,
  )

  if (!response.ok) {
    throw new Error(
      `Unable to load opening hours (${response.status})`,
    )
  }

  return response.json() as Promise<OpeningHour[]>
}