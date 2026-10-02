import { useEffect, useState } from "react"

import { AgendaToolbar } from "@/components/agenda/agenda-toolbar"
import { DayAgenda } from "@/components/agenda/day-agenda"
import {
  getAppointmentsForDate,
  getOpeningHours,
  type AppointmentAgenda,
  type OpeningHour,
} from "@/lib/api"

export function AgendaPage() {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [appointments, setAppointments] = useState<AppointmentAgenda[]>([])
  const [openingHours, setOpeningHours] = useState<OpeningHour[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // L'API attend une date locale au format YYYY-MM-DD.
    const targetDate = selectedDate.toLocaleDateString("en-CA")

    async function loadAgenda() {
      try {
        setIsLoading(true)
        setError(null)

        const data = await getAppointmentsForDate(1, targetDate)
        setAppointments(data)

        const hours = await getOpeningHours(1)

        // JavaScript utilise dimanche = 0, alors que notre backend
        // utilise lundi = 0. On convertit donc les deux conventions.
        const weekday = (selectedDate.getDay() + 6) % 7

        const selectedDayOpeningHours = hours.filter(
          (openingHour) => openingHour.weekday === weekday,
        )

        setOpeningHours(selectedDayOpeningHours)
      } catch {
        setError("Impossible de charger l'agenda.")
      } finally {
        setIsLoading(false)
      }
    }

    void loadAgenda()
  }, [selectedDate])

  function changeDay(offset: number) {
    setSelectedDate((currentDate) => {
      const nextDate = new Date(currentDate)
      nextDate.setDate(nextDate.getDate() + offset)
      return nextDate
    })
  }

  return (
    <main className="flex flex-1 flex-col gap-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          Agenda
        </h1>

        <p className="text-muted-foreground">
          Consultez et gérez les rendez-vous de votre activité.
        </p>
      </div>

      <AgendaToolbar
        selectedDate={selectedDate}
        onPreviousDay={() => changeDay(-1)}
        onToday={() => setSelectedDate(new Date())}
        onNextDay={() => changeDay(1)}
      />

      {!isLoading && !error && (
        <p className="text-sm text-muted-foreground">
          <span className="font-medium text-foreground">
            {appointments.length}
          </span>
          {" rendez-vous dans la journée"}
        </p>
      )}

      {isLoading && (
        <p className="text-sm text-muted-foreground">
          Chargement de l&apos;agenda...
        </p>
      )}

      {error && (
        <p className="text-sm text-destructive">
          {error}
        </p>
      )}

      {!isLoading && !error && (
        <DayAgenda
            appointments={appointments}
            openingHours={openingHours}
        />
        )}
    </main>
  )
}