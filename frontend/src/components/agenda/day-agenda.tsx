import type {
  AppointmentAgenda,
  OpeningHour,
} from "@/lib/api"

type DayAgendaProps = {
  appointments: AppointmentAgenda[]
  openingHours: OpeningHour[]
}

// Une heure occupe 96 px dans la grille.
const HOUR_HEIGHT = 96
const MINUTE_HEIGHT = HOUR_HEIGHT / 60

function timeToMinutes(value: string) {
  const [hours, minutes] = value.split(":").map(Number)

  return hours * 60 + minutes
}

function formatMinutes(minutes: number) {
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60

  return `${String(hours).padStart(2, "0")}:${String(
    remainingMinutes,
  ).padStart(2, "0")}`
}

function getAppointmentPosition(
  appointment: AppointmentAgenda,
  agendaStartMinutes: number,
) {
  const start = new Date(appointment.start_datetime)
  const end = new Date(appointment.end_datetime)

  const appointmentStartMinutes =
    start.getHours() * 60 + start.getMinutes()

  const durationMinutes =
    (end.getTime() - start.getTime()) / 60_000

  return {
    top:
      (appointmentStartMinutes - agendaStartMinutes) *
      MINUTE_HEIGHT,
    height: durationMinutes * MINUTE_HEIGHT,
  }
}

function formatTime(dateTime: string) {
  return new Intl.DateTimeFormat("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateTime))
}

export function DayAgenda({
  appointments,
  openingHours,
}: DayAgendaProps) {
  if (openingHours.length === 0) {
    return (
      <div className="rounded-lg border p-6 text-sm text-muted-foreground">
        Entreprise fermée ce jour.
      </div>
    )
  }

  // La grille commence à la première ouverture et se termine
  // à la dernière fermeture de la journée.
  const agendaStartMinutes = Math.min(
    ...openingHours.map((openingHour) =>
      timeToMinutes(openingHour.start_time),
    ),
  )

  const agendaEndMinutes = Math.max(
    ...openingHours.map((openingHour) =>
      timeToMinutes(openingHour.end_time),
    ),
  )

  const agendaDurationMinutes =
    agendaEndMinutes - agendaStartMinutes

  const agendaHeight =
    agendaDurationMinutes * MINUTE_HEIGHT

  // Repères horaires affichés sur le côté de la grille.
  const firstHour = Math.ceil(agendaStartMinutes / 60) * 60

  const hourMarkers: number[] = []

  for (
    let minute = firstHour;
    minute < agendaEndMinutes;
    minute += 60
  ) {
    hourMarkers.push(minute)
  }

  // On ajoute explicitement l'heure de fermeture afin qu'elle
  // soit toujours visible, même si elle ne tombe pas sur une heure ronde.
  hourMarkers.push(agendaEndMinutes)

  return (
    <div className="overflow-hidden rounded-lg border">
      <div className="grid grid-cols-[5rem_1fr]">
        {/* Colonne des heures */}
        <div className="relative border-r">
          {hourMarkers.map((minute) => (
            <div
              key={minute}
              className="absolute right-3 text-sm text-muted-foreground"
              style={{
                top:
                  (minute - agendaStartMinutes) *
                  MINUTE_HEIGHT,
                transform:
                  minute === agendaStartMinutes
                    ? "translateY(0)"
                    : minute === agendaEndMinutes
                      ? "translateY(-100%)"
                      : "translateY(-50%)",
              }}
            >
              {formatMinutes(minute)}
            </div>
          ))}
        </div>

        {/* Zone principale de l'agenda */}
        <div
          className="relative"
          style={{ height: agendaHeight }}
        >
          {/* Lignes correspondant aux repères horaires */}
          {hourMarkers.map((minute) => (
            <div
              key={minute}
              className="absolute inset-x-0 border-t"
              style={{
                top:
                  (minute - agendaStartMinutes) *
                  MINUTE_HEIGHT,
              }}
            />
          ))}

          {/* Rendez-vous positionnés selon leur heure et leur durée */}
          {appointments.map((appointment) => {
            const { top, height } = getAppointmentPosition(
              appointment,
              agendaStartMinutes,
            )

            return (
              <div
                key={appointment.id}
                className="absolute left-2 right-2 overflow-hidden rounded-md border bg-card px-3 py-2 shadow-sm"
                style={{
                  top,
                  height,
                }}
              >
                <p className="font-medium">
                  {formatTime(appointment.start_datetime)}
                  {" – "}
                  {formatTime(appointment.end_datetime)}
                  {" · "}
                  {appointment.customer_name}
                </p>

                <p className="text-sm text-muted-foreground">
                  {appointment.service_name}
                  {" · "}
                  {appointment.staff_first_name}
                  {appointment.staff_last_name
                    ? ` ${appointment.staff_last_name}`
                    : ""}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}